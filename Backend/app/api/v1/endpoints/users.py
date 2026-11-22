from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.core.permissions import RoleChecker
from app.core.security import get_password_hash
from app.services.audit_services import log_action

router = APIRouter()

class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role_id: int

class UserUpdateRequest(BaseModel):
    is_active: bool | None = None
    role_id: int | None = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role_id: int
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN"]))
):
    return db.query(User).all()

@router.post("/", response_model=UserResponse)
def create_user(
    req: UserCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN"]))
):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    new_user = User(
        username=req.username,
        email=req.email,
        password_hash=get_password_hash(req.password),
        role_id=req.role_id,
        is_active=True,
        must_change_password=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_action(
        db=db, action="CREATE_USER", resource_type="USER", outcome="SUCCESS",
        actor_user_id=current_user.id, resource_id=str(new_user.id), request=request,
        details={"username": new_user.username, "role_id": new_user.role_id}
    )
    return new_user

@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    req: UserUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ADMIN"]))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    changes = {}
    if req.is_active is not None:
        changes["is_active"] = {"old": user.is_active, "new": req.is_active}
        user.is_active = req.is_active
    if req.role_id is not None:
        changes["role_id"] = {"old": user.role_id, "new": req.role_id}
        user.role_id = req.role_id

    db.commit()
    db.refresh(user)

    log_action(
        db=db, action="UPDATE_USER", resource_type="USER", outcome="SUCCESS",
        actor_user_id=current_user.id, resource_id=str(user.id), request=request,
        details={"changes": changes}
    )
    return user