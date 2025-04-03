from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class modeloUsuario(BaseModel):
    email: str = Field(..., pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', example="gabriel.mzn@gmail.com")
    password: str = Field(..., min_length=8, example="qwer1234!")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()} 