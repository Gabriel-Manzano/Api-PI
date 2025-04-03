from DB.conexion import Base
from sqlalchemy import Column, Integer, String, DateTime, func

class User(Base):

    __tablename__ = 'tbUsers'
    
    id = Column(Integer, primary_key="True", autoincrement="auto")
    email = Column(String)
    password = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())