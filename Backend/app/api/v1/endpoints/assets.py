from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.asset import Asset
from app.models.baseline import Baseline
from app.models.baseline_item import BaselineItem
from app.core.permissions import RoleChecker
from app.services.audit_services import log_action

router = APIRouter()

# --- Esquemas ---
class AssetResponse(BaseModel):
    id: int
    repository_id: int
    category_id: Optional[int]
    relative_path: str
    file_name: str
    mime_type: Optional[str]
    size_bytes: int
    is_active: bool
    first_seen_at: datetime

    class Config:
        from_attributes = True

class AssetUpdateRequest(BaseModel):
    category_id: Optional[int] = None
    file_name: Optional[str] = None
    is_active: Optional[bool] = None
    mime_type: Optional[str] = None

class AssetWithBaselineResponse(AssetResponse):
    expected_sha256: Optional[str] = None

# --- Endpoints ---

@router.get("/repository/{repository_id}", response_model=List[AssetResponse])
def list_assets_by_repository(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "OPERADOR", "AUDITOR", "VIEWER"]))
):
    """Visualizar todos los archivos registrados en un repositorio."""
    assets = db.query(Asset).filter(
        Asset.repository_id == repository_id,
        Asset.is_active == True
    ).all()
    return assets

@router.get("/{asset_id}/detail", response_model=AssetWithBaselineResponse)
def get_asset_detail(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "OPERADOR", "AUDITOR", "VIEWER"]))
):
    """Obtiene los detalles del asset y su hash esperado en la línea base activa."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    # Buscar la línea base activa del repositorio
    active_baseline = db.query(Baseline).filter(
        Baseline.repository_id == asset.repository_id,
        Baseline.status == "ACTIVE"
    ).first()

    expected_sha = None
    if active_baseline:
        item = db.query(BaselineItem).filter(
            BaselineItem.baseline_id == active_baseline.id,
            BaselineItem.relative_path == asset.relative_path
        ).first()
        if item:
            expected_sha = item.sha256

    # Construir respuesta
    asset_dict = asset.__dict__.copy()
    asset_dict["expected_sha256"] = expected_sha
    return asset_dict

@router.patch("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int,
    req: AssetUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "OPERADOR"]))
):
    """
    Modifica los metadatos lógicos de un archivo (categoría, nombre visible, estado).
    NO modifica el archivo físico en el sistema de archivos.
    """
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        log_action(
            db=db, action="UPDATE_ASSET_METADATA", resource_type="ASSET", outcome="FAILURE",
            actor_user_id=current_user.id, resource_id=str(asset_id), request=Request,
            details={"reason": "Asset no encontrado"}
        )
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    changes = {}
    if req.category_id is not None:
        changes["category_id"] = {"old": asset.category_id, "new": req.category_id}
        asset.category_id = req.category_id
    if req.file_name is not None:
        changes["file_name"] = {"old": asset.file_name, "new": req.file_name}
        asset.file_name = req.file_name
    if req.is_active is not None:
        changes["is_active"] = {"old": asset.is_active, "new": req.is_active}
        asset.is_active = req.is_active
    if req.mime_type is not None:
        changes["mime_type"] = {"old": asset.mime_type, "new": req.mime_type}
        asset.mime_type = req.mime_type

    db.commit()
    db.refresh(asset)

    # Auditoría de la modificación (operación crítica)
    log_action(
        db=db, action="UPDATE_ASSET_METADATA", resource_type="ASSET",
        resource_id=str(asset.id), outcome="SUCCESS", actor_user_id=current_user.id,
        details={"changes": req.model_dump(exclude_unset=True)}
    )

    return asset