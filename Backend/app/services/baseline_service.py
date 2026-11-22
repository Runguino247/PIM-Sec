import json
import os
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.baseline import Baseline
from app.models.baseline_item import BaselineItem
from app.models.asset import Asset
from app.models.repository import Repository
from app.models.user import User
from app.fim.hashing import calculate_sha256
from app.fim.hmac_manager import generate_baseline_hmac
from app.utils.file_validation import resolve_safe_path
from app.services.audit_services import log_action
from datetime import datetime

def create_baseline_proposal(db: Session, repository_id: int, reason: str, current_user: User):
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repositorio no encontrado")

    # Obtener la última versión
    last_baseline = db.query(Baseline).filter(Baseline.repository_id == repository_id).order_by(Baseline.version_no.desc()).first()
    next_version = 1 if not last_baseline else last_baseline.version_no + 1

    # Crear cabecera de línea base (PROPOSED)
    new_baseline = Baseline(
        repository_id=repository_id,
        version_no=next_version,
        status="PROPOSED",
        created_by=current_user.id,
        reason=reason
    )
    db.add(new_baseline)
    db.flush() # Para obtener el ID

    # Recorrer el repositorio y calcular hashes
    items_data = []
    for root, _, files in os.walk(repo.root_path):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, repo.root_path)
            try:
                sha256 = calculate_sha256(abs_path)
                size = os.path.getsize(abs_path)
                
                # Crear item de baseline
                item = BaselineItem(
                    baseline_id=new_baseline.id,
                    relative_path=rel_path,
                    sha256=sha256,
                    size_bytes=size
                )
                db.add(item)
                items_data.append({"relative_path": rel_path, "sha256": sha256, "size": size})
            except Exception as e:
                print(f"Error procesando {abs_path}: {e}")

    # Calcular HMAC sobre los datos canónicos
    hmac_signature = generate_baseline_hmac(items_data)
    new_baseline.hmac_sha256 = hmac_signature

    log_action(
        db=db, action="CREATE_BASELINE_PROPOSAL", resource_type="BASELINE",
        resource_id=str(new_baseline.id), outcome="SUCCESS", actor_user_id=current_user.id
    )
    db.commit()
    db.refresh(new_baseline)
    return new_baseline


def approve_baseline(db: Session, baseline_id: int, approve: bool, current_user: User, reason: str = None):
    baseline = db.query(Baseline).filter(Baseline.id == baseline_id).first()
    if not baseline:
        raise HTTPException(status_code=404, detail="Línea base no encontrada")
    if baseline.status != "PROPOSED":
        raise HTTPException(status_code=400, detail="Solo se pueden aprobar líneas base en estado PROPOSED")
    if baseline.created_by == current_user.id:
        raise HTTPException(status_code=403, detail="El creador no puede aprobar su propia línea base")

    if approve:
        # Si hay una anterior ACTIVE, pasarla a SUPERSEDED
        active_baseline = db.query(Baseline).filter(
            Baseline.repository_id == baseline.repository_id,
            Baseline.status == "ACTIVE"
        ).first()
        if active_baseline:
            active_baseline.status = "SUPERSEDED"
        
        baseline.status = "ACTIVE"
        baseline.approved_by = current_user.id
        baseline.approved_at = datetime.utcnow()
    else:
        baseline.status = "REJECTED"

    log_action(
        db=db, action="APPROVE_BASELINE", resource_type="BASELINE",
        resource_id=str(baseline.id), outcome="SUCCESS", actor_user_id=current_user.id,
        details={"approved": approve, "reason": reason}
    )
    db.commit()
    return baseline