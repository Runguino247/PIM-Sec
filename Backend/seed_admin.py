from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.core.security import get_password_hash

def create_admin():
    db = SessionLocal()
    try:
        # Buscar rol ADMIN
        admin_role = db.query(Role).filter(Role.code == "ADMIN").first()
        if not admin_role:
            print("Error: El rol ADMIN no existe. Verifica las migraciones.")
            return

        # Verificar si ya existe
        if db.query(User).filter(User.username == "admin").first():
            print("El usuario 'admin' ya existe.")
            return

        # Crear usuario
        admin_user = User(
            role_id=admin_role.id,
            username="admin",
            email="oscarreyesbarja@gmail.com",
            password_hash=get_password_hash("admin123"),
            is_active=True,
            must_change_password=True
        )
        db.add(admin_user)
        db.commit()
        print("✅ Usuario 'admin' creado exitosamente. Contraseña: admin123")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()