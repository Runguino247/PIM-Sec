from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserResponse
from app.core.permissions import get_current_user
from app.core.security import get_password_hash, verify_password, create_access_token
from app.services.audit_services import log_action
from pydantic import BaseModel

router = APIRouter()

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 1. Buscar usuario
    user = db.query(User).filter(User.username == form_data.username).first()
    
    ip_addr = request.client.host if request.client else None

    # 2. Validar usuario y contraseña
    if not user or not verify_password(form_data.password, user.password_hash):        # Registrar intento fallido
        log_action(
            db=db, action="LOGIN_ATTEMPT", resource_type="AUTH", outcome="FAILURE",
            source_ip=ip_addr, details={"username": form_data.username, "reason": "Credenciales inválidas"}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        log_action(
            db=db, action="LOGIN_ATTEMPT", resource_type="AUTH", outcome="DENIED",
            actor_user_id=user.id, source_ip=ip_addr, details={"reason": "Cuenta inactiva"}
        )
        raise HTTPException(status_code=400, detail="Cuenta desactivada")

    # 3. Actualizar último login
    user.last_login_at = datetime.utcnow()
    db.commit()

    # 4. Generar Token JWT
    access_token = create_access_token(subject=user.id)
    
    # 5. Registrar éxito en auditoría
    log_action(
        db=db, action="LOGIN_ATTEMPT", resource_type="AUTH", outcome="SUCCESS",
        actor_user_id=user.id, source_ip=ip_addr
    )

    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "must_change_password": user.must_change_password
    }

@router.post("/logout")
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # En un sistema real, aquí revocarías el refresh_token
    log_action(
        db=db, action="LOGOUT", resource_type="AUTH", outcome="SUCCESS",
        actor_user_id=current_user.id, request=request
    )
    return {"message": "Sesión cerrada correctamente"}


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Endpoint protegido para validar que el token funciona."""
    return current_user

@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    
    current_user.password_hash = get_password_hash(req.new_password)
    current_user.must_change_password = False
    db.commit()

    log_action(
        db=db, action="CHANGE_PASSWORD", resource_type="USER",
        resource_id=str(current_user.id), outcome="SUCCESS", actor_user_id=current_user.id
    )
    return {"message": "Contraseña actualizada correctamente"}

