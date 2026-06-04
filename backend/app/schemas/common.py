from pydantic import BaseModel
from typing import Any, Optional, List
from math import ceil


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None


def success_response(data: Any = None, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


def error_response(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None}


def paginated_response(items: list, total: int, page: int, page_size: int) -> dict:
    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": ceil(total / page_size) if page_size > 0 else 0,
        },
    }
