from fastapi import FastAPI
from DB.conexion import engine, Base
from routers.usuario import routerUsuario
from routers.news_routes import router
from models.modelsDB import Role
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="API PI")


Base.metadata.create_all(bind=engine)


def insert_roles():
    from sqlalchemy.orm import Session
    session = Session(bind=engine)

    if session.query(Role).count() == 0:  
        admin_role = Role(name="admin")
        user_role = Role(name="usuario")
        session.add(admin_role)
        session.add(user_role)
        session.commit()
        print("Roles insertados correctamente")
    else:
        print("Los roles ya existen")
    
    session.close()


insert_roles()

app.include_router(routerUsuario)
app.include_router(router, prefix="/news")


origins = [
    "http://127.0.0.1:8000",
   
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=10000, reload=True)