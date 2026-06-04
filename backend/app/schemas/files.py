from pydantic import BaseModel
from typing import Optional, List, Any


class FileUploadResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    file_type: str
    status: str
    total_rows: Optional[int] = None
    total_columns: Optional[int] = None
    columns: Optional[List[str]] = None
    created_at: str


class FileStatusResponse(BaseModel):
    id: str
    filename: str
    status: str
    total_rows: Optional[int] = None
    total_columns: Optional[int] = None
    columns: Optional[List[str]] = None
    dedup_removed_count: Optional[int] = None
    dedup_total_before: Optional[int] = None
    dedup_total_after: Optional[int] = None
    dedup_columns: Optional[List[str]] = None
    dedup_strategy: Optional[str] = None
    created_at: str
    updated_at: str


class FileHistoryResponse(BaseModel):
    items: List[FileStatusResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PreviewResponse(BaseModel):
    id: str
    filename: str
    columns: List[str]
    rows: List[dict]
    total_rows: int
    preview_rows: int


class DedupRequest(BaseModel):
    columns: Optional[List[str]] = None
    strategy: str = "keep_first"  # keep_first, keep_last


class DedupResponse(BaseModel):
    id: str
    total_before: int
    total_after: int
    removed_count: int
    columns_used: List[str]
    strategy: str
    created_at: str


class DedupPreviewResponse(BaseModel):
    id: str
    original_columns: List[str]
    dedup_columns: List[str]
    strategy: str
    total_before: int
    total_after: int
    removed_count: int
    columns: List[str]
    rows: List[dict]
    preview_rows: int


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None
