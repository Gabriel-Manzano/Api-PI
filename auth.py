import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException
from datetime import datetime, timedelta
def createToken(data: dict):
    exp = datetime.utcnow() + timedelta(days=7)
    payload = data.copy()
    payload.update({"exp": exp})
    token: str = jwt.encode(payload=payload,  key='secretKey', algorithm='HS256')
    return token

# Función para validar el token
def validateToken(token: str):
    try:
        data: dict = jwt.decode(token, key='secretKey', algorithms=['HS256'])
        return data
    except ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token Expirado")
    except InvalidTokenError:
        raise HTTPException(status_code=403, detail="Token no autorizado")
