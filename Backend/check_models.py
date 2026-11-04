from app.db.base import Base
import app.models

print("TABLAS REGISTRADAS EN SQLALCHEMY")
print("--------------------------------")

for table_name in sorted(Base.metadata.tables):
    print(table_name)

print("--------------------------------")
print(f"Total de tablas: {len(Base.metadata.tables)}")