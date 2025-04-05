from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary, func
from sqlalchemy.orm import relationship
from DB.conexion import Base
from sqlalchemy import UniqueConstraint

class Role(Base):
    __tablename__ = 'tbRoles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = 'tbUsers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)  # Añadir `username`
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)  # Para almacenar la contraseña cifrada
    role_id = Column(Integer, ForeignKey("tbRoles.id"), nullable=False, default=2)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
 
    role_id = Column(Integer, ForeignKey("tbRoles.id"), nullable=False, default=2)  # Por defecto rol de usuario
    role = relationship("Role", back_populates="users")
    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
class Post(Base):
    __tablename__ = 'tbPosts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('tbUsers.id')) 
    created_at = Column(DateTime, default=func.now())
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    image = Column(LargeBinary) 
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)

    user = relationship("User", back_populates="posts")
    
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = 'tbComments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('tbPosts.id')) 
    user_id = Column(Integer, ForeignKey('tbUsers.id')) 
    created_at = Column(DateTime, default=func.now())
    description = Column(String, nullable=False)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    
    # Relación con post
    post = relationship("Post", back_populates="comments")
    
    # Relación con usuario
    user = relationship("User", back_populates="comments")


class Like(Base):
    __tablename__ = 'tbLikes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('tbUsers.id'))  
    post_id = Column(Integer, ForeignKey('tbPosts.id'))  

    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)
    
    user = relationship("User")
    post = relationship("Post")

