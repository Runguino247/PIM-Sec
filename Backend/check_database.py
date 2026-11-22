from sqlalchemy import inspect
from app.db.session import engine

inspector = inspect(engine)

tables = inspector.get_table_names(schema="public")

tables = [
    table for table in tables
    if table != "alembic_version"
]

print("\n========== PIM-Sec ==========")
print("TABLAS EN POSTGRESQL")
print("============================")

for index, table in enumerate(sorted(tables), start=1):
    print(f"{index:02d}. {table}")

print("============================")
print(f"Total de tablas: {len(tables)}")

if len(tables) == 17:
    print("VERIFICACIÓN: CORRECTA")
else:
    print("VERIFICACIÓN: REVISAR ESQUEMA")