from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, baselines, scans, repositories, assets, events, alerts, changes, audit, dashboard
# Aquí irás importando tus endpoints a medida que los crees
# from app.api.v1.endpoints import auth, users, repositories...

api_router = APIRouter()

# api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

# Autenticacion y gestión de usuarios
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(users.router, prefix="/users", tags=["Usuarios"])
api_router.include_router(baselines.router, prefix="/baselines", tags=["Líneas Base"])
api_router.include_router(scans.router, prefix="/scans", tags=["Escaneos FIM"])
api_router.include_router(repositories.router, prefix="/repositories", tags=["Repositorios"])
api_router.include_router(assets.router, prefix="/assets", tags=["Archivos"])

# Gestión de eventos y alertas
api_router.include_router(events.router, prefix="/events", tags=["Eventos"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alertas"])
api_router.include_router(events.router, prefix="/events", tags=["Eventos"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alertas"])
api_router.include_router(changes.router, prefix="/changes", tags=["Cambios Autorizados"])


api_router.include_router(audit.router, prefix="/audit", tags=["Auditoría"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])