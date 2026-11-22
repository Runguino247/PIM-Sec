import os
from fastapi import HTTPException

def validate_relative_path(relative_path: str):
    """Valida que la ruta sea relativa y no intente salir del directorio."""
    if relative_path.startswith("/") or relative_path.startswith("\\"):
        raise HTTPException(status_code=400, detail="La ruta debe ser relativa")
    if ".." in relative_path:
        raise HTTPException(status_code=400, detail="La ruta no puede contener '..'")

def resolve_safe_path(base_path: str, relative_path: str) -> str:
    """Resuelve la ruta absoluta y verifica que esté dentro del base_path."""
    validate_relative_path(relative_path)
    absolute_path = os.path.abspath(os.path.join(base_path, relative_path))
    if not absolute_path.startswith(os.path.abspath(base_path)):
        raise HTTPException(status_code=403, detail="Acceso denegado fuera del repositorio")
    return absolute_path