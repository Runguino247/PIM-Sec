from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
from app.models.alert import Alert
from app.models.alert_history import AlertHistory
from app.models.user import User
from app.services.audit_services import log_action

def acknowledge_alert(db: Session, alert_id: int, current_user: User):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    if alert.status != "NEW":
        raise HTTPException(status_code=400, detail="Solo se pueden reconocer alertas en estado NEW")

    previous = alert.status
    alert.status = "ACKNOWLEDGED"
    alert.acknowledged_at = datetime.utcnow()
    alert.assigned_to = current_user.id

    history = AlertHistory(
        alert_id=alert.id, changed_by=current_user.id,
        previous_status=previous, new_status="ACKNOWLEDGED",
        note="Alerta reconocida", changed_at=datetime.utcnow()
    )
    db.add(history)
    db.commit()
    db.refresh(alert)

    log_action(
        db=db, action="ACKNOWLEDGE_ALERT", resource_type="ALERT",
        resource_id=str(alert.id), outcome="SUCCESS", actor_user_id=current_user.id
    )
    return alert

def resolve_alert(db: Session, alert_id: int, resolution_note: str, current_user: User):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    if alert.status != "ACKNOWLEDGED":
        raise HTTPException(status_code=400, detail="La alerta debe estar ACKNOWLEDGED antes de resolverse")
    if not resolution_note or not resolution_note.strip():
        raise HTTPException(status_code=400, detail="Se requiere una nota de resolución")

    previous = alert.status
    alert.status = "RESOLVED"
    alert.resolved_at = datetime.utcnow()
    alert.resolution_note = resolution_note

    history = AlertHistory(
        alert_id=alert.id, changed_by=current_user.id,
        previous_status=previous, new_status="RESOLVED",
        note=resolution_note, changed_at=datetime.utcnow()
    )
    db.add(history)
    db.commit()
    db.refresh(alert)

    log_action(
        db=db, action="RESOLVE_ALERT", resource_type="ALERT",
        resource_id=str(alert.id), outcome="SUCCESS", actor_user_id=current_user.id,
        details={"note": resolution_note}
    )
    return alert