from ipaddress import IPv4Address

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.db.session import get_db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.core.permissions import RoleChecker

router = APIRouter()

class AuditResponse(BaseModel):
    id: int
    actor_user_id: int | None
    action: str
    resource_type: str
    resource_id: str | None
    occurred_at: datetime
    source_ip: str | None | IPv4Address
    outcome: str
    details_json: dict | None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[AuditResponse])
def list_audit_logs(
    actor_user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "AUDITOR"])) # Solo ADMIN y AUDITOR
):
    # Consulta el historial de auditoría con filtros. Solo ADMIN y AUDITOR.
    query = db.query(AuditLog)

    if actor_user_id:
        query = query.filter(AuditLog.actor_user_id == actor_user_id)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if start_date:
        query = query.filter(AuditLog.occurred_at >= start_date)

    return query.order_by(AuditLog.occurred_at.desc()).limit(limit).all()