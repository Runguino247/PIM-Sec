from sqlalchemy.orm import Session
from datetime import datetime
from app.models.security_event import SecurityEvent
from app.models.alert import Alert
from app.models.scan_result import ScanResult

# Mapeo de resultado de escaneo a tipo de evento y severidad (Sección 12.4)
EVENT_MAPPING = {
    "MODIFIED": {"event_type": "FILE_MODIFIED", "severity": "HIGH"},
    "DELETED": {"event_type": "FILE_DELETED", "severity": "HIGH"},
    "NEW": {"event_type": "FILE_NEW", "severity": "MEDIUM"},
    "REPLACED": {"event_type": "FILE_REPLACED", "severity": "HIGH"},
    "ERROR": {"event_type": "FILE_CHECK_ERROR", "severity": "LOW"}
}

def process_scan_results(db: Session, scan_id: int, repository_id: int):
    """
    Lee los resultados del escaneo, genera eventos para las desviaciones
    y crea alertas automáticas (Regla de la sección 12.4).
    """
    results = db.query(ScanResult).filter(ScanResult.scan_id == scan_id).all()
    events_created = 0

    for result in results:
        if result.result in EVENT_MAPPING:
            mapping = EVENT_MAPPING[result.result]
            
            # 1. Crear Evento de Seguridad
            event = SecurityEvent(
                scan_id=scan_id,
                repository_id=repository_id,
                scan_result_id=result.id,
                event_type=mapping["event_type"],
                severity=mapping["severity"],
                expected_sha256=result.expected_sha256,
                actual_sha256=result.actual_sha256,
                detected_at=datetime.utcnow(),
                actor_user_id=None, # Desconocido por defecto (no atribuir al que lanzó el escaneo)
                details_json={"relative_path": result.relative_path}
            )
            db.add(event)
            db.flush() # Para obtener el event.id

            # 2. Crear Alerta asociada (NEW)
            alert = Alert(
                event_id=event.id,
                status="NEW",
                created_at=datetime.utcnow()
            )
            db.add(alert)
            events_created += 1

    db.commit()
    return events_created