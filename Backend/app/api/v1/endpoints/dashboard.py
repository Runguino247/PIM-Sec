from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.repository import Repository
from app.models.alert import Alert
from app.models.integrity_scan import IntegrityScan
from app.core.permissions import RoleChecker

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "OPERADOR", "AUDITOR", "VIEWER"]))
):
    """Resumen general para el dashboard."""
    total_repos = db.query(Repository).filter(Repository.is_active == True).count()
    open_alerts = db.query(Alert).filter(Alert.status != "RESOLVED").count()
    last_scan = db.query(IntegrityScan).order_by(IntegrityScan.started_at.desc()).first()

    return {
        "total_repositories": total_repos,
        "open_alerts": open_alerts,
        "last_scan": {
            "id": last_scan.id if last_scan else None,
            "status": last_scan.status if last_scan else None,
            "started_at": last_scan.started_at if last_scan else None,
            "summary": last_scan.summary_json if last_scan else None
        } if last_scan else None
    }