from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.models.integrity_scan import IntegrityScan
from app.db.session import get_db
from app.models.user import User
from app.schemas.scan import ScanRequest, ScanResponse
from app.fim.scanner import run_scan
from app.services.audit_services import log_action
from app.core.permissions import RoleChecker
from typing import List

router = APIRouter()

@router.post("/run", response_model=ScanResponse)
def execute_scan(
    req: ScanRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "OPERADOR"]))
):
    try:
        scan = run_scan(db, req.repository_id, req.baseline_id, current_user.id)
        log_action(
            db=db, action="RUN_MANUAL_SCAN", resource_type="SCAN", outcome="SUCCESS",
            actor_user_id=current_user.id, resource_id=str(scan.id), request=Request,
            details={"repository_id": req.repository_id, "summary": scan.summary_json}
        )
        return scan
    except HTTPException as e:
        log_action(
            db=db, action="RUN_MANUAL_SCAN", resource_type="SCAN", outcome="FAILURE",
            actor_user_id=current_user.id, request=Request,
            details={"repository_id": req.repository_id, "error": e.detail}
        )
        raise e
    
@router.get("/history/{repository_id}", response_model=List[ScanResponse])
def get_scan_history(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "OPERADOR", "AUDITOR", "VIEWER"]))
):
    scans = db.query(IntegrityScan).filter(
        IntegrityScan.repository_id == repository_id
    ).order_by(IntegrityScan.started_at.desc()).limit(20).all()
    return scans