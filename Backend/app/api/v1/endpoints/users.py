from fastapi import APIRouter, Depends
from app.core.permissions import RoleChecker
from app.models.user import User

router = APIRouter()

# Solo el rol ADMIN puede acceder a este endpoint
@router.get("/admin-only")
def admin_dashboard(current_user: User = Depends(RoleChecker(["ADMIN"]))):
    return {"message": "Bienvenido Administrador. Tienes acceso a la gestión de usuarios."}