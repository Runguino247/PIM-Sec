from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.alert import Alert
from app.core.permissions import RoleChecker
from app.services.alert_services import acknowledge_alert, resolve_alert
from app.services.audit_services import log_action

router = APIRouter()

class AlertResponse(BaseModel):
    id: int
    event_id: int
    status: str
    assigned_to: Optional[int]
    created_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    resolution_note: Optional[str]

    class Config:
        from_attributes = True

class ResolveRequest(BaseModel):
    resolution_note: str

@router.get("/", response_model=List[AlertResponse])
def list_alerts(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "OPERADOR", "AUDITOR", "VIEWER"]))
):
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    return query.order_by(Alert.created_at.desc()).limit(100).all()

@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge(
    alert_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "OPERADOR", "AUDITOR"]))
):
    try:
        alert = acknowledge_alert(db, alert_id, current_user)
        log_action(
            db=db, action="ACKNOWLEDGE_ALERT", resource_type="ALERT", outcome="SUCCESS",
            actor_user_id=current_user.id, resource_id=str(alert_id), request=request
        )
        return alert
    except HTTPException as e:
        log_action(
            db=db, action="ACKNOWLEDGE_ALERT", resource_type="ALERT", outcome="FAILURE",
            actor_user_id=current_user.id, resource_id=str(alert_id), request=request,
            details={"reason": e.detail}
        )
        raise e
