from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class DedupRequest(BaseModel):
    columns: List[str] = Field(..., min_length=1)
    strategy: str = Field(default="keep_first", pattern="^(keep_first|keep_last)$")
