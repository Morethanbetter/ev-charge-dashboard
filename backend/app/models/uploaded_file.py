import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    dataset_name = Column(String(255))
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    row_count = Column(Integer)
    column_count = Column(Integer)
    columns_ = Column("columns", JSONB)
    status = Column(String(20), default="processing", index=True)
    dedup_status = Column(String(20), default="pending")
    total_rows = Column(Integer)
    duplicate_rows = Column(Integer)
    unique_rows = Column(Integer)
    dedup_columns = Column(JSONB)
    dedup_strategy = Column(String(20), default="keep_first")
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    processed_at = Column(DateTime(timezone=True))

    @property
    def columns(self):
        return self.columns_
