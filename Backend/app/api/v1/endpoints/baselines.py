from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.models.baseline import Baseline
from app.db.session import get_db
from app.models.user import User
from app.schemas.baseline import BaselineCreateRequest, BaselineApproveRequest, BaselineResponse
from app.services.baseline_service import create_baseline_proposal, approve_baseline
from app.core.permissions import get_current_user, RoleChecker
from typing import List
from app.services.audit_services import log_action

router = APIRouter()

@router.post("/propose", response_model=BaselineResponse)
def propose_baseline(
    req: BaselineCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "OPERADOR"]))
):
    try:
        baseline = create_baseline_proposal(db, req.repository_id, req.reason, current_user)
        log_action(
            db=db, action="PROPOSE_BASELINE", resource_type="BASELINE", outcome="SUCCESS",
            actor_user_id=current_user.id, resource_id=str(baseline.id), request=Request,
            details={"repository_id": req.repository_id, "version_no": baseline.version_no}
        )
        return baseline
    except Exception as e:
        log_action(
            db=db, action="PROPOSE_BASELINE", resource_type="BASELINE", outcome="FAILURE",
            actor_user_id=current_user.id, request=Request,
            details={"repository_id": req.repository_id, "error": str(e)}
        )
        raise e
    
    
@router.post("/{baseline_id}/approve", response_model=BaselineResponse)
def approve_baseline_endpoint(
    baseline_id: int,
    req: BaselineApproveRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN"]))
):
    try:
        baseline = approve_baseline(db, baseline_id, req.approve, current_user, req.reason)
        log_action(
            db=db, action="APPROVE_BASELINE" if req.approve else "REJECT_BASELINE",
            resource_type="BASELINE", outcome="SUCCESS",
            actor_user_id=current_user.id, resource_id=str(baseline.id), request=request,
            details={"decision": baseline.status, "reason": req.reason}
        )
        return baseline
    except HTTPException as e:
        log_action(
            db=db, action="APPROVE_BASELINE_ATTEMPT", resource_type="BASELINE", outcome="DENIED",
            actor_user_id=current_user.id, resource_id=str(baseline_id), request=request,
            details={"reason": e.detail}
        )
        raise e

@router.get("/repository/{repository_id}", response_model=List[BaselineResponse])
def get_baselines_by_repository(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "OPERADOR", "AUDITOR", "VIEWER"]))
):
    """Lista todas las versiones de línea base de un repositorio."""
    baselines = db.query(Baseline).filter(
        Baseline.repository_id == repository_id
    ).order_by(Baseline.version_no.desc()).all()
    return baselines