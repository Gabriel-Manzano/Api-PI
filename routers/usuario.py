from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from modelsPydantic import modeloUsuario
from DB.conexion import Session
from models.modelsDB import User
from fastapi import APIRouter
from pydantic import BaseModel
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException
from datetime import datetime, timedelta
routerUsuario = APIRouter()

# Nuevo modelo para las credenciales de login
class modeloCredenciales(BaseModel):
    email: str
    password: str

# Endponit consultar todos

@routerUsuario.get('/usuarios', tags=['Operaciones CRUD'])
def leerUsuarios():
    db = Session()
    try:
        consulta = db.query(User).all()
        return JSONResponse(content= jsonable_encoder(consulta))

    except Exception as e:
        return JSONResponse(status_code=500, content ={"message": "Error al guardar el usuario", "Exception": str(e)})

    finally:
        db.close()

#Endpoint buscar por id

@routerUsuario.get('/usuarios/{id}', tags=['Operaciones CRUD'])
def leerUno(id: int):
    db = Session()
    try:
        usuario = db.query(User).filter(User.id == id).first()

        if not usuario:

            return JSONResponse(status_code=404, content={"message": "Usuario no encontrado"})

        return JSONResponse(status_code=200, content=jsonable_encoder(usuario))

    except Exception as e:

        return JSONResponse(status_code=500, content={"message": "Error al consultar", "Exception": str(e)})
    
    finally:

        db.close()


# Endponit Agregar nuevos

@routerUsuario.post('/usuarios', response_model= modeloUsuario, tags=['Operaciones CRUD'])
def agregarUsuarios(usuario:modeloUsuario):
    db = Session()
    try: 
        db.add(User(**usuario.model_dump()))
        db.commit()
        return JSONResponse(status_code=201, content ={"message": "Usuario Guardado", "usuario": usuario.model_dump()})
 
    except Exception as e:

        db.rollback()
        return JSONResponse(status_code=500, content ={"message": "Error al guardar el usuario", "Exception": str(e)})
    
    finally:
        
        db.close()

# Endponit Actualizar

@routerUsuario.put('/usuarios/{id}', response_model=modeloUsuario, tags=['Operaciones CRUD'])
def actualizarUsuarios(id: int, usuario: modeloUsuario):
    try:
        db = Session()
        usuario_actualizado = db.query(User).filter(User.id == id).first()
        
        if not usuario_actualizado:

            return JSONResponse(status_code=500, content={"message": "Usuario no encontrado"})

        for key, value in usuario.model_dump().items():

            setattr(usuario_actualizado, key, value)

        db.commit()
        db.refresh(usuario_actualizado)

        return JSONResponse(status_code=200, content={"message": "Usuario actualizado", "usuario": usuario.model_dump()})

    except Exception as e:

        db.rollback()
        return JSONResponse(status_code=500, content={"message": "Error al actualizar el usuario", "Exception": str(e)})
    
    finally: db.close()

# Endponit Eliminar

@routerUsuario.delete('/usuarios/{id}', tags=['Operaciones CRUD'])
def eliminarUsuario(id: int):
    try:
        db = Session()
        usuario_eliminado = db.query(User).filter(User.id == id).first()

        if not usuario_eliminado:
            return JSONResponse(status_code=404, content={"message": "Usuario no encontrado"})

        db.delete(usuario_eliminado)
        db.commit()

        return JSONResponse(status_code=200, content={"message": "Usuario eliminado"})

    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"message": "Error al eliminar el usuario", "Exception": str(e)})

    finally:
        db.close()



SECRET_KEY = "mi_secreto" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def createToken(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token: str = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return token


def validateToken(token: str):
    try:
        data: dict = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return data
    except ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token Expirado")
    except InvalidTokenError:
        raise HTTPException(status_code=403, detail="Token no autorizado")
    


# Nuevo endpoint para autenticación (login)
@routerUsuario.post('/login', tags=['Autenticacion'])
def login(credenciales: modeloCredenciales):
    db = Session()
    try:
        usuario = db.query(User).filter(User.email == credenciales.email).first()
        if not usuario:
            return JSONResponse(status_code=404, content={"message": "Usuario no encontrado"})
        if usuario.password != credenciales.password:
            return JSONResponse(status_code=401, content={"message": "Credenciales inválidas"})
        token = createToken({"sub": usuario.email})
        return JSONResponse(status_code=200, content={"token": token})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Error al autenticar", "Exception": str(e)})
    finally:
        db.close()