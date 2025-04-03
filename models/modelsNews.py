from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary, func
from sqlalchemy.orm import relationship
from DB.conexion import Base
from sqlalchemy import UniqueConstraint
class Post(Base):
    __tablename__ = 'tbPosts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('tbUsers.id'))
    created_at = Column(DateTime, default=func.now())
    title = Column(String)
    description = Column(String)
    image = Column(LargeBinary)  # Puede ser None si no se envía imagen
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    
    # Relación con comentarios
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = 'tbComments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('tbPosts.id'))
    user_id = Column(Integer, ForeignKey('tbUsers.id'))
    created_at = Column(DateTime, default=func.now())
    description = Column(String)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    
    post = relationship("Post", back_populates="comments")



class Like(Base):
    __tablename__ = 'tbLikes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('tbUsers.id'))
    post_id = Column(Integer, ForeignKey('tbPosts.id'))

    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)
