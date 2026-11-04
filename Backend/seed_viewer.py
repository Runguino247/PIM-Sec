from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.core.security import get_password_hash

def create_viewer():
    db = SessionLocal()
    try:
        # Buscar rol viewer
        viewer_role = db.query(Role).filter(Role.code == "VIEWER").first()
        if not viewer_role:
            print("Error: El rol viewer no existe. Verifica las migraciones.")
            return

        # Verificar si ya existe
        if db.query(User).filter(User.username == "viewer").first():
            print("El usuario 'viewer' ya existe.")
            return

        # Crear usuario
        viewer_user = User(
            role_id=viewer_role.id,
            username="viewer",
            email="oscarreyesbarja1@gmail.com",
            password_hash=get_password_hash("viewer123"),
            is_active=True,
            must_change_password=True
        )
        db.add(viewer_user)
        db.commit()
        print("✅ Usuario 'viewer' creado exitosamente. Contraseña: viewer123")
    finally:
        db.close()

if __name__ == "__main__":
    create_viewer()