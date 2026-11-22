from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.authorized_change import AuthorizedChange
from app.core.permissions import RoleChecker
from app.services.change_services import request_change, decide_change, link_event_to_change
from app.services.audit_services import log_action

router = APIRouter()

class ChangeCreateRequest(BaseModel):
    repository_id: int
    scope_json: dict
    reason: str
    valid_from: datetime
    valid_until: datetime

class ChangeDecisionRequest(BaseModel):
    approve: bool
    decision_note: Optional[str] = None

class ChangeResponse(BaseModel):
    id: int
    repository_id: int
    requested_by: int
    approved_by: Optional[int]
    status: str
    reason: str
    valid_from: datetime
    valid_until: datetime
    created_at: datetime
    decided_at: Optional[datetime]

    class Config:
        from_attributes = True

@router.post("/", response_model=ChangeResponse)
def create_change_request(
    req: ChangeCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "OPERADOR"]))
):
    change = request_change(db, req.repository_id, req.scope_json, req.reason, req.valid_from, req.valid_until, current_user)
    log_action(
        db=db, action="REQUEST_AUTHORIZED_CHANGE", resource_type="AUTHORIZED_CHANGE", outcome="SUCCESS",
        actor_user_id=current_user.id, resource_id=str(change.id), request=request,
        details={"repository_id": req.repository_id, "scope": req.scope_json}
    )
    return change

@router.post("/{change_id}/decide", response_model=ChangeResponse)
def decide(
    change_id: int,
    req: ChangeDecisionRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN"]))  # Solo ADMIN aprueba cambios
):
    try:
        change = decide_change(db, change_id, req.approve, req.decision_note, current_user)
        log_action(
            db=db, action="APPROVE_CHANGE" if req.approve else "REJECT_CHANGE",
            resource_type="AUTHORIZED_CHANGE", outcome="SUCCESS",
            actor_user_id=current_user.id, resource_id=str(change_id), request=request,
            details={"decision_note": req.decision_note}
        )
        return change
    except HTTPException as e:
        log_action(
            db=db, action="DECIDE_CHANGE_ATTEMPT", resource_type="AUTHORIZED_CHANGE", outcome="DENIED",
            actor_user_id=current_user.id, resource_id=str(change_id), request=request,
            details={"reason": e.detail}
        )
        raise e
    
@router.post("/{change_id}/link-event/{event_id}")
def link_event(
    change_id: int,
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "OPERADOR", "AUDITOR"]))
):
    link_event_to_change(db, change_id, event_id, current_user)
    log_action(
        db=db, action="LINK_EVENT_TO_CHANGE", resource_type="AUTHORIZED_CHANGE", outcome="SUCCESS",
        actor_user_id=current_user.id, resource_id=str(change_id), request=request,
        details={"event_id": event_id}
    )
    return {"message": "Evento vinculado correctamente"}