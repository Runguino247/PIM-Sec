from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
from app.models.authorized_change import AuthorizedChange
from app.models.change_event_link import ChangeEventLink
from app.models.user import User
from app.services.audit_services import log_action

def request_change(db: Session, repository_id: int, scope_json: dict, reason: str,
                   valid_from: datetime, valid_until: datetime, current_user: User):
    change = AuthorizedChange(
        repository_id=repository_id, requested_by=current_user.id,
        scope_json=scope_json, reason=reason,
        valid_from=valid_from, valid_until=valid_until,
        status="PENDING"
    )
    db.add(change)
    db.commit()
    db.refresh(change)

    log_action(
        db=db, action="REQUEST_CHANGE", resource_type="AUTHORIZED_CHANGE",
        resource_id=str(change.id), outcome="SUCCESS", actor_user_id=current_user.id
    )
    return change

def decide_change(db: Session, change_id: int, approve: bool, decision_note: str, current_user: User):
    change = db.query(AuthorizedChange).filter(AuthorizedChange.id == change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if change.status != "PENDING":
        raise HTTPException(status_code=400, detail="Solo se pueden decidir solicitudes PENDING")
    if change.requested_by == current_user.id:
        raise HTTPException(status_code=403, detail="El solicitante no puede aprobar su propia solicitud")
    if not approve and (not decision_note or not decision_note.strip()):
        raise HTTPException(status_code=400, detail="Se requiere nota al rechazar")

    change.status = "APPROVED" if approve else "REJECTED"
    change.decided_by = current_user.id
    change.decided_at = datetime.utcnow()
    change.decision_note = decision_note
    if approve:
        change.approved_by = current_user.id

    db.commit()
    db.refresh(change)

    log_action(
        db=db, action="DECIDE_CHANGE", resource_type="AUTHORIZED_CHANGE",
        resource_id=str(change.id), outcome="SUCCESS", actor_user_id=current_user.id,
        details={"approved": approve, "note": decision_note}
    )
    return change

def link_event_to_change(db: Session, change_id: int, event_id: int, current_user: User):
    change = db.query(AuthorizedChange).filter(AuthorizedChange.id == change_id).first()
    if not change or change.status != "APPROVED":
        raise HTTPException(status_code=400, detail="La solicitud debe estar APPROVED para vincular eventos")
    
    existing = db.query(ChangeEventLink).filter(
        ChangeEventLink.authorized_change_id == change_id,
        ChangeEventLink.event_id == event_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="El evento ya está vinculado a esta solicitud")

    link = ChangeEventLink(
        authorized_change_id=change_id, event_id=event_id,
        linked_by=current_user.id, linked_at=datetime.utcnow()
    )
    db.add(link)
    db.commit()

    log_action(
        db=db, action="LINK_EVENT_TO_CHANGE", resource_type="AUTHORIZED_CHANGE",
        resource_id=str(change_id), outcome="SUCCESS", actor_user_id=current_user.id,
        details={"event_id": event_id}
    )
    return link