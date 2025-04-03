from fastapi import FastAPI
from DB.conexion import engine,Base
from routers.usuario import routerUsuario

app= FastAPI(
    title= 'API PI',
)

app.include_router(routerUsuario)

Base.metadata.create_all(bind=engine)