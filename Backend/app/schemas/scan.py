from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class ScanRequest(BaseModel):
    repository_id: int
    baseline_id: int

class ScanResponse(BaseModel):
    id: int
    repository_id: int
    baseline_id: int
    status: str
    files_checked: int
    started_at: datetime
    finished_at: Optional[datetime] = None
    summary_json: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True