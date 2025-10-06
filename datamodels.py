from pydantic import BaseModel
from typing import List, Optional


class ResponseItem(BaseModel):
    id: int
    requirement: str
    is_met: Optional[bool] = None
    citation: Optional[str] = None
    explanation: Optional[str] = None
