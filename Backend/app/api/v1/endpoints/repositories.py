from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.models.user import User
from app.models.repository import Repository
from app.core.permissions import RoleChecker
from typing import List
from datetime import datetime
from app.services.audit_services import log_action

router = APIRouter()

class RepositoryCreate(BaseModel):
    name: str
    root_path: str
    description: str | None = None

class RepositoryResponse(BaseModel):
    id: int
    name: str
    root_path: str
    description: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

router = APIRouter()



@router.post("/", response_model=RepositoryResponse)
def create_repository(
    req: RepositoryCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "OPERADOR"]))
):
    existing = db.query(Repository).filter(Repository.root_path == req.root_path).first()
    if existing:
        log_action(
            db=db, action="CREATE_REPOSITORY", resource_type="REPOSITORY", outcome="FAILURE",
            actor_user_id=current_user.id, request=request, details={"reason": "Ruta duplicada", "root_path": req.root_path}
        )
        raise HTTPException(status_code=400, detail="Ya existe un repositorio con esa ruta")

    new_repo = Repository(
        name=req.name,
        root_path=req.root_path,
        description=req.description,
        created_by=current_user.id
    )
    db.add(new_repo)
    db.commit()
    db.refresh(new_repo)

    log_action(
        db=db,
        action="CREATE_REPOSITORY",
        resource_type="REPOSITORY",
        outcome="SUCCESS",
        actor_user_id=current_user.id,
        resource_id=str(new_repo.id),
        request=request,
        details={
            "name": new_repo.name,
            "root_path": new_repo.root_path
        }
    )
    return new_repo

@router.get("/", response_model=List[RepositoryResponse])
def list_repositories(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN", "OPERADOR", "AUDITOR", "VIEWER"]))
):
    # Todos los roles pueden consultar el inventario de repositorios
    return db.query(Repository).all()