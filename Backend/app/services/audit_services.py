from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog # Ajusta según tu modelo
from fastapi import Request

def log_action(
    db: Session,
    action: str,
    resource_type: str,
    outcome: str,
    actor_user_id: int | None = None,
    resource_id: str | None = None,
    details: dict | None = None,
    request: Request | None = None,
    source_ip: str | None = None  # <-- Parámetro aceptado
):
    """
    Registra una acción en la tabla de auditoría (append-only).
    Extrae automáticamente la IP del cliente si se pasa el Request.
    """
    source_ip = None
    
    # if request and request.client:
    #     print(f"\n\n\nRequest client: {request.client.host_port}\n\n\n")
    #     source_ip = request.client.host_port

    audit_entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        source_ip=source_ip,
        outcome=outcome,
        details_json=details
    )
    db.add(audit_entry)
    db.commit()