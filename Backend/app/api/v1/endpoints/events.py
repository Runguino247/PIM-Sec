from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.db.session import get_db
from app.models.user import User
from app.models.security_event import SecurityEvent
from app.core.permissions import RoleChecker

router = APIRouter()

class EventResponse(BaseModel):
    id: int
    scan_id: int
    repository_id: int
    event_type: str
    severity: str
    expected_sha256: Optional[str]
    actual_sha256: Optional[str]
    detected_at: datetime
    details_json: Optional[dict]

    class Config:
        from_attributes = True

@router.get("/", response_model=List[EventResponse])
def list_events(
    repository_id: Optional[int] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "OPERADOR", "AUDITOR", "VIEWER"]))
):
    query = db.query(SecurityEvent)
    if repository_id:
        query = query.filter(SecurityEvent.repository_id == repository_id)
    if severity:
        query = query.filter(SecurityEvent.severity == severity)
    return query.order_by(SecurityEvent.detected_at.desc()).limit(100).all()