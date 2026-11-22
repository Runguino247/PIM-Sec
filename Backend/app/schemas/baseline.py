from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class BaselineCreateRequest(BaseModel):
    repository_id: int
    reason: str

class BaselineResponse(BaseModel):
    id: int
    repository_id: int
    version_no: int
    status: str
    created_by: int
    created_at: datetime
    reason: str
    hmac_sha256: Optional[str] = None

    class Config:
        from_attributes = True

class BaselineApproveRequest(BaseModel):
    approve: bool  # True para ACTIVE, False para REJECTED
    reason: Optional[str] = None