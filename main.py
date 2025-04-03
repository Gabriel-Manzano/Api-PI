from fastapi import FastAPI
from DB.conexion import engine, Base
from routers.usuario import routerUsuario
from routers.news_routes import router

app = FastAPI(title="API PI")

app.include_router(routerUsuario)
app.include_router(router, prefix="/news")

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)