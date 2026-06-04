import os
import uuid
import json
import asyncio
from datetime import datetime, timezone
from typing import Optional, List, Tuple

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc

from app.core.config import get_settings
from app.models.uploaded_file import UploadedFile

settings = get_settings()
ALLOWED_EXTENSIONS = {".csv", ".json", ".xlsx", ".xls"}


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def validate_file_extension(filename: str) -> bool:
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def load_dedup_data(file_id: str) -> Optional[dict]:
    dedup_path = os.path.join(settings.dedup_dir, f"{file_id}_dedup.json")
    if not os.path.exists(dedup_path):
        return None
    with open(dedup_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_dedup_data(file_id: str, data: dict):
    dedup_path = os.path.join(settings.dedup_dir, f"{file_id}_dedup.json")
    with open(dedup_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, default=str)


def parse_file_sync(file_path: str, filename: str):
    ext = get_file_extension(filename)
    if ext == ".csv":
        df = pd.read_csv(file_path, encoding="utf-8-sig")
    elif ext == ".json":
        df = pd.read_json(file_path)
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported format: {ext}")
    return df


async def process_file_task(file_id: str, file_path: str, filename: str):
    from app.core.database import async_session
    async with async_session() as db:
        try:
            result = await db.execute(select(UploadedFile).where(UploadedFile.id == uuid.UUID(file_id)))
            file_record = result.scalar_one_or_none()
            if not file_record:
                return

            df = parse_file_sync(file_path, filename)
            columns = df.columns.tolist()
            row_count = len(df)

            file_record.columns_ = columns
            file_record.column_count = len(columns)
            file_record.row_count = row_count
            file_record.total_rows = row_count

            # Auto dedup on all columns (keep_first)
            df_dedup = df.drop_duplicates(keep="first")
            unique_count = len(df_dedup)
            dup_count = row_count - unique_count

            file_record.unique_rows = unique_count
            file_record.duplicate_rows = dup_count
            file_record.dedup_columns = columns
            file_record.dedup_strategy = "keep_first"
            file_record.status = "completed"
            file_record.dedup_status = "completed"
            file_record.processed_at = datetime.now(timezone.utc)

            # Build dedup data with duplicate info
            seen = {}
            duplicates = []
            for idx, row in df.iterrows():
                key = tuple(str(row[col]) for col in columns)
                if key in seen:
                    duplicates.append({"row_index": idx, "duplicate_of_row": seen[key]})
                else:
                    seen[key] = idx

            dedup_data = {
                "columns": columns,
                "rows": df.to_dict(orient="records"),
                "duplicates": duplicates,
            }
            save_dedup_data(file_id, dedup_data)
            await db.commit()

        except Exception as e:
            if file_record:
                file_record.status = "failed"
                file_record.error_message = str(e)
                await db.commit()


async def save_upload_file(upload_file, user_id: int, db: AsyncSession) -> UploadedFile:
    filename = upload_file.filename
    file_id = uuid.uuid4()
    file_path = os.path.join(settings.upload_dir, f"{file_id}_{filename}")
    content = await upload_file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    uploaded = UploadedFile(
        id=file_id,
        user_id=user_id,
        filename=filename,
        dataset_name=filename.rsplit(".", 1)[0],
        file_path=file_path,
        file_size=len(content),
        status="processing",
        dedup_status="pending",
    )
    db.add(uploaded)
    await db.commit()
    await db.refresh(uploaded)
    asyncio.create_task(process_file_task(str(file_id), file_path, filename))
    return uploaded


async def get_file_by_id(file_id: str, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(UploadedFile).where(UploadedFile.id == uuid.UUID(file_id), UploadedFile.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_file_history(user_id, db, page=1, page_size=20, keyword=None, status=None, dedup_status=None, sort_by="created_at", sort_order="desc"):
    query = select(UploadedFile).where(UploadedFile.user_id == user_id)
    if keyword:
        query = query.where(UploadedFile.filename.ilike(f"%{keyword}%"))
    if status:
        query = query.where(UploadedFile.status == status)
    if dedup_status:
        query = query.where(UploadedFile.dedup_status == dedup_status)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    sort_col = getattr(UploadedFile, sort_by, UploadedFile.created_at)
    query = query.order_by(desc(sort_col) if sort_order == "desc" else asc(sort_col))
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all(), total


async def rerun_dedup_task(file_id: str, columns: list, strategy: str):
    import pandas as pd
    from app.core.database import async_session
    async with async_session() as db:
        try:
            result = await db.execute(select(UploadedFile).where(UploadedFile.id == uuid.UUID(file_id)))
            file = result.scalar_one_or_none()
            if not file:
                return
            dedup_data = load_dedup_data(file_id)
            if not dedup_data:
                file.dedup_status = "completed"
                await db.commit()
                return

            all_rows = dedup_data.get("rows", [])
            df = pd.DataFrame(all_rows)
            seen = {}
            duplicates = []
            for idx, row in df.iterrows():
                key = tuple(str(row[col]) for col in columns)
                if strategy == "keep_last":
                    if key in seen:
                        duplicates.append({"row_index": seen[key], "duplicate_of_row": idx})
                    seen[key] = idx
                else:
                    if key in seen:
                        duplicates.append({"row_index": idx, "duplicate_of_row": seen[key]})
                    else:
                        seen[key] = idx

            file.unique_rows = len(df) - len(duplicates)
            file.duplicate_rows = len(duplicates)
            file.dedup_status = "completed"
            dedup_data["duplicates"] = duplicates
            save_dedup_data(file_id, dedup_data)
            await db.commit()
        except Exception as e:
            if file:
                file.dedup_status = "completed"
                file.error_message = str(e)
                await db.commit()
