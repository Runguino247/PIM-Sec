from fastapi import APIRouter
from app.api.v1.endpoints import auth, users
# Aquí irás importando tus endpoints a medida que los crees
# from app.api.v1.endpoints import auth, users, repositories...

api_router = APIRouter()

# api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

# Autenticacion y gestión de usuarios
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(users.router, prefix="/users", tags=["Usuarios"])
