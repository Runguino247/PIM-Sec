import os
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.baseline import Baseline
from app.models.baseline_item import BaselineItem
from app.models.integrity_scan import IntegrityScan
from app.models.scan_result import ScanResult
from app.models.security_event import SecurityEvent
from app.models.repository import Repository
from app.fim.hashing import calculate_sha256
from app.fim.hmac_manager import verify_baseline_hmac
from fastapi import HTTPException
from app.services.event_service import process_scan_results
    
def run_scan(db: Session, repository_id: int, baseline_id: int, initiated_by: int = None):
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    baseline = db.query(Baseline).filter(Baseline.id == baseline_id).first()

    if not repo or not baseline:
        raise HTTPException(status_code=404, detail="Repositorio o línea base no encontrados")
    if baseline.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Solo se puede escanear contra una línea base ACTIVE")

    # 1. Crear el registro del escaneo PRIMERO (estado RUNNING)
    # Esto nos permite tener el scan_id para vincular el evento si algo falla.
    scan = IntegrityScan(
        repository_id=repo.id, 
        baseline_id=baseline.id,
        initiated_by=initiated_by, 
        status="RUNNING"
    )
    db.add(scan)
    db.flush() # Obtenemos el scan.id

    # 2. Validar HMAC de la línea base
    items = db.query(BaselineItem).filter(BaselineItem.baseline_id == baseline.id).all()
    items_data = [{"relative_path": i.relative_path, "sha256": i.sha256, "size": i.size_bytes} for i in items]
    
    if not verify_baseline_hmac(items_data, baseline.hmac_sha256):
        # Si el HMAC falla, actualizamos el escaneo a FAILED
        scan.status = "FAILED"
        scan.finished_at = datetime.utcnow()
        
        # Generamos el evento vinculado al scan_id
        event = SecurityEvent(
            scan_id=scan.id,  # <--- AHORA SÍ TENEMOS EL ID
            repository_id=repo.id, 
            event_type="BASELINE_HMAC_INVALID",
            severity="CRITICAL", 
            detected_at=datetime.utcnow(),
            details_json={"baseline_id": baseline.id, "reason": "HMAC inválido"}
        )
        db.add(event)
        db.commit()
        
        # Lanzamos la excepción para que el cliente sepa que falló
        raise HTTPException(status_code=500, detail="HMAC de línea base inválido. Escaneo abortado.")

    # 3. Mapear archivos esperados y actuales
    expected_files = {item.relative_path: item for item in items}
    found_files = set()
    
    summary = {"INTACT": 0, "MODIFIED": 0, "DELETED": 0, "NEW": 0, "ERROR": 0}

    # 4. Escanear directorio actual
    for root, _, files in os.walk(repo.root_path):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, repo.root_path)
            found_files.add(rel_path)

            try:
                actual_sha256 = calculate_sha256(abs_path)
            except Exception as e:
                result = ScanResult(
                    scan_id=scan.id, relative_path=rel_path, result="ERROR",
                    error_message=str(e), checked_at=datetime.utcnow()
                )
                db.add(result)
                summary["ERROR"] += 1
                continue

            if rel_path in expected_files:
                expected_item = expected_files[rel_path]
                if actual_sha256 == expected_item.sha256:
                    result_type = "INTACT"
                else:
                    result_type = "MODIFIED"
                
                result = ScanResult(
                    scan_id=scan.id, baseline_item_id=expected_item.id,
                    relative_path=rel_path, expected_sha256=expected_item.sha256,
                    actual_sha256=actual_sha256, result=result_type,
                    checked_at=datetime.utcnow()
                )
                db.add(result)
                summary[result_type] += 1
            else:
                result = ScanResult(
                    scan_id=scan.id, relative_path=rel_path,
                    actual_sha256=actual_sha256, result="NEW",
                    checked_at=datetime.utcnow()
                )
                db.add(result)
                summary["NEW"] += 1

    # 5. Detectar eliminados (estaban en baseline pero no en disco)
    for rel_path, expected_item in expected_files.items():
        if rel_path not in found_files:
            result = ScanResult(
                scan_id=scan.id, baseline_item_id=expected_item.id,
                relative_path=rel_path, expected_sha256=expected_item.sha256,
                result="DELETED", checked_at=datetime.utcnow()
            )
            db.add(result)
            summary["DELETED"] += 1

    # 6. Finalizar escaneo exitosamente
    scan.status = "COMPLETED"
    scan.finished_at = datetime.utcnow()
    scan.files_checked = sum(summary.values())
    scan.summary_json = summary
    db.commit() # Guardamos los scan_results primero
    # Procesar resultados y generar eventos/alertas
    process_scan_results(db, scan.id, repo.id)    
    return scan
