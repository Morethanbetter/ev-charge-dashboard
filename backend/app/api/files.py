import os
import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.user import User
from app.models.uploaded_file import UploadedFile
from app.schemas.common import success_response, paginated_response
from app.schemas.file import DedupRequest
from app.services.file_service import (
    validate_file_extension, save_upload_file, get_file_by_id,
    get_file_history, load_dedup_data, rerun_dedup_task,
)

router = APIRouter()
settings = get_settings()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not validate_file_extension(file.filename):
        raise HTTPException(status_code=400, detail={"code": 2001, "message": "不支持的文件格式", "data": None})
    content = await file.read()
    await file.seek(0)
    if len(content) > settings.max_file_size:
        raise HTTPException(status_code=413, detail={"code": 2002, "message": "文件大小超过限制（50MB）", "data": None})
    uploaded = await save_upload_file(file, current_user.id, db)
    if dataset_name:
        uploaded.dataset_name = dataset_name
        from sqlalchemy import update
        await db.execute(update(UploadedFile).where(UploadedFile.id == uploaded.id).values(dataset_name=dataset_name))
        await db.commit()
    return success_response(
        data={
            "file_id": str(uploaded.id), "filename": uploaded.filename,
            "dataset_name": uploaded.dataset_name, "file_size": uploaded.file_size,
            "row_count": uploaded.row_count, "column_count": uploaded.column_count,
            "columns": uploaded.columns_, "status": uploaded.status,
            "dedup_status": uploaded.dedup_status, "created_at": uploaded.created_at.isoformat(),
        },
        message="文件上传成功",
    )


@router.get("/history")
async def get_history(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None, status: Optional[str] = None,
    dedup_status: Optional[str] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|filename|file_size)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    files, total = await get_file_history(current_user.id, db, page, page_size, keyword, status, dedup_status, sort_by, sort_order)
    items = [
        {
            "file_id": str(f.id), "filename": f.filename, "dataset_name": f.dataset_name,
            "file_size": f.file_size, "row_count": f.row_count, "column_count": f.column_count,
            "status": f.status, "dedup_status": f.dedup_status,
            "duplicate_rows": f.duplicate_rows, "unique_rows": f.unique_rows,
            "created_at": f.created_at.isoformat(),
            "processed_at": f.processed_at.isoformat() if f.processed_at else None,
        }
        for f in files
    ]
    return paginated_response(items, total, page, page_size)


@router.get("/{file_id}/status")
async def get_file_status(file_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    file = await get_file_by_id(file_id, current_user.id, db)
    if not file:
        raise HTTPException(status_code=404, detail={"code": 2005, "message": "文件不存在", "data": None})
    progress = 100 if file.status == "completed" else 0
    return success_response(data={
        "file_id": str(file.id), "filename": file.filename, "status": file.status,
        "dedup_status": file.dedup_status, "progress": progress,
        "total_rows": file.total_rows, "duplicate_rows": file.duplicate_rows,
        "unique_rows": file.unique_rows, "error_message": file.error_message,
        "processed_at": file.processed_at.isoformat() if file.processed_at else None,
    })


@router.get("/{file_id}/download")
async def download_file(file_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    file = await get_file_by_id(file_id, current_user.id, db)
    if not file or not os.path.exists(file.file_path):
        raise HTTPException(status_code=404, detail={"code": 2005, "message": "文件不存在", "data": None})
    return FileResponse(path=file.file_path, filename=file.filename, media_type="application/octet-stream")


@router.delete("/{file_id}")
async def delete_file(file_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    file = await get_file_by_id(file_id, current_user.id, db)
    if not file:
        raise HTTPException(status_code=404, detail={"code": 2005, "message": "文件不存在", "data": None})
    if file.status == "processing":
        raise HTTPException(status_code=400, detail={"code": 2006, "message": "文件正在处理中，无法删除", "data": None})
    if os.path.exists(file.file_path):
        os.remove(file.file_path)
    dedup_path = os.path.join(settings.dedup_dir, f"{file_id}_dedup.json")
    if os.path.exists(dedup_path):
        os.remove(dedup_path)
    await db.delete(file)
    await db.commit()
    return success_response(message="文件已删除")


@router.get("/{file_id}/preview")
async def preview_file(
    file_id: str, limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    file = await get_file_by_id(file_id, current_user.id, db)
    if not file:
        raise HTTPException(status_code=404, detail={"code": 2005, "message": "文件不存在", "data": None})
    dedup_data = load_dedup_data(file_id)
    if not dedup_data:
        raise HTTPException(status_code=400, detail={"code": 2003, "message": "文件内容解析失败", "data": None})
    columns = dedup_data.get("columns", [])
    all_rows = dedup_data.get("rows", [])
    sliced = all_rows[offset:offset + limit]
    rows = [[row.get(col) for col in columns] for row in sliced]
    return success_response(data={"columns": columns, "total_rows": len(all_rows), "offset": offset, "limit": limit, "rows": rows})


@router.get("/{file_id}/dedup")
async def get_dedup_result(
    file_id: str, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    type: str = Query("all", pattern="^(all|unique|duplicate)$"),
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    file = await get_file_by_id(file_id, current_user.id, db)
    if not file:
        raise HTTPException(status_code=404, detail={"code": 2005, "message": "文件不存在", "data": None})
    if file.dedup_status != "completed":
        raise HTTPException(status_code=400, detail={"code": 2007, "message": "去重处理尚未完成", "data": None})
    dedup_data = load_dedup_data(file_id)
    if not dedup_data:
        raise HTTPException(status_code=400, detail={"code": 2007, "message": "去重处理尚未完成", "data": None})
    columns = dedup_data.get("columns", [])
    all_rows = dedup_data.get("rows", [])
    duplicates = dedup_data.get("duplicates", [])
    dup_indices = {d["row_index"] for d in duplicates}
    dup_map = {d["row_index"]: d["duplicate_of_row"] for d in duplicates}
    items = []
    for idx, row in enumerate(all_rows):
        is_dup = idx in dup_indices
        if type == "unique" and is_dup:
            continue
        if type == "duplicate" and not is_dup:
            continue
        items.append({"row_index": idx, "data": {col: row.get(col) for col in columns}, "is_duplicate": is_dup, "duplicate_of_row": dup_map.get(idx)})
    total = len(items)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    paged = items[(page - 1) * page_size:page * page_size]
    total_rows = file.total_rows or len(all_rows)
    unique_rows = file.unique_rows or (total_rows - len(duplicates))
    dup_rate = round((len(duplicates) / total_rows * 100) if total_rows > 0 else 0, 2)
    return success_response(data={
        "file_id": str(file.id), "dedup_status": file.dedup_status,
        "summary": {"total_rows": total_rows, "unique_rows": unique_rows, "duplicate_rows": len(duplicates), "dedup_rate": dup_rate, "dedup_columns": file.dedup_columns or columns, "strategy": file.dedup_strategy or "keep_first"},
        "items": paged, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages,
    })


@router.post("/{file_id}/dedup")
async def rerun_dedup(file_id: str, req: DedupRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    file = await get_file_by_id(file_id, current_user.id, db)
    if not file:
        raise HTTPException(status_code=404, detail={"code": 2005, "message": "文件不存在", "data": None})
    if file.status == "processing":
        raise HTTPException(status_code=400, detail={"code": 2006, "message": "文件正在处理中", "data": None})
    file_columns = file.columns_ or []
    for col in req.columns:
        if col not in file_columns:
            raise HTTPException(status_code=400, detail={"code": 2008, "message": f"指定的列名不存在: {col}", "data": None})
    from sqlalchemy import update
    await db.execute(update(UploadedFile).where(UploadedFile.id == file.id).values(dedup_status="processing", dedup_columns=req.columns, dedup_strategy=req.strategy))
    await db.commit()
    import asyncio
    asyncio.create_task(rerun_dedup_task(str(file.id), req.columns, req.strategy))
    return success_response(data={"file_id": str(file.id), "dedup_status": "processing", "columns": req.columns, "strategy": req.strategy}, message="去重任务已提交")


@router.get("/{file_id}/dedup/download")
async def download_dedup(
    file_id: str, format: str = Query("csv", pattern="^(csv|json|xlsx)$"),
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    file = await get_file_by_id(file_id, current_user.id, db)
    if not file:
        raise HTTPException(status_code=404, detail={"code": 2005, "message": "文件不存在", "data": None})
    if file.dedup_status != "completed":
        raise HTTPException(status_code=400, detail={"code": 2007, "message": "去重处理尚未完成", "data": None})
    dedup_data = load_dedup_data(file_id)
    if not dedup_data:
        raise HTTPException(status_code=400, detail={"code": 2007, "message": "去重处理尚未完成", "data": None})
    columns = dedup_data.get("columns", [])
    all_rows = dedup_data.get("rows", [])
    duplicates = dedup_data.get("duplicates", [])
    dup_indices = {d["row_index"] for d in duplicates}
    unique_rows = [row for idx, row in enumerate(all_rows) if idx not in dup_indices]
    import pandas as pd
    df = pd.DataFrame(unique_rows)
    output_path = os.path.join(settings.dedup_dir, f"{file_id}_dedup_export.{format}")
    if format == "csv":
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        media_type, ext = "text/csv", "csv"
    elif format == "json":
        df.to_json(output_path, orient="records", force_ascii=False)
        media_type, ext = "application/json", "json"
    else:
        df.to_excel(output_path, index=False)
        media_type, ext = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "xlsx"
    return FileResponse(path=output_path, filename=f"{file.dataset_name}_dedup.{ext}", media_type=media_type)
