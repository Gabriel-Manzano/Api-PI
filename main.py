from fastapi import FastAPI
from DB.conexion import engine, Base
from routers.usuario import routerUsuario
from routers.news_routes import router
from models.modelsDB import Role

app = FastAPI(title="API PI")

# Crear las tablas de la base de datos
Base.metadata.create_all(bind=engine)

# Verificar si los roles ya existen y si no insertarlos
def insert_roles():
    from sqlalchemy.orm import Session
    session = Session(bind=engine)

    if session.query(Role).count() == 0:  # Verificar si no hay roles
        # Insertar roles por defecto: admin y usuario
        admin_role = Role(name="admin")
        user_role = Role(name="usuario")

        session.add(admin_role)
        session.add(user_role)
        session.commit()
        print("Roles insertados correctamente")
    else:
        print("Los roles ya existen")
    
    session.close()

# Insertar roles después de crear las tablas
insert_roles()

# Incluir rutas en FastAPI
app.include_router(routerUsuario)
app.include_router(router, prefix="/news")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)
