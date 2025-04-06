from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import base64
from DB.conexion import Session as SessionLocal
from models.modelsDB import Post, Comment, NewsLike, NewsDislike, CommentLike, CommentDislike
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/news", tags=["News"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelos Pydantic para Posts y Comments
class PostCreate(BaseModel):
    user_id: int
    title: str
    description: str
    image: Optional[bytes] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class CommentCreate(BaseModel):
    user_id: int
    description: str

class CommentUpdate(BaseModel):
    description: Optional[str] = None

# ---------- Endpoints para Posts ----------

@router.post("/posts")
def create_post(
    user_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    image_data = image.file.read() if image else None
    
    new_post = Post(
        user_id=user_id,
        title=title,
        description=description,
        image=image_data
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"message": "Post creado", "post_id": new_post.id}

@router.get("/posts", response_model=List[dict])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    posts_data = [{
        "id": p.id,
        "user_id": p.user_id,
        "created_at": p.created_at.isoformat(),
        "title": p.title,
        "description": p.description,
        "likes": p.likes,
        "dislikes": p.dislikes,
        "image": base64.b64encode(p.image).decode('utf-8') if p.image else None
    } for p in posts]
    return posts_data

@router.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    return {
        "id": post.id,
        "user_id": post.user_id,
        "created_at": post.created_at.isoformat(),
        "title": post.title,
        "description": post.description,
        "likes": post.likes,
        "dislikes": post.dislikes,
        "image": base64.b64encode(post.image).decode('utf-8') if post.image else None
    }

@router.put("/posts/{post_id}")
async def update_post(
    post_id: int,
    user_id: Optional[int] = Form(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    likes: Optional[int] = Form(None),
    dislikes: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    if user_id is not None:
        post.user_id = user_id
    if title is not None:
        post.title = title
    if description is not None:
        post.description = description
    if likes is not None:
        post.likes = likes
    if dislikes is not None:
        post.dislikes = dislikes
    if image and image.filename and image.content_type and image.content_type.startswith("image/"):
        post.image = await image.read()

    db.commit()
    db.refresh(post)

    return {
        "message": "Post actualizado correctamente",
        "post": {
            "id": post.id,
            "user_id": post.user_id,
            "title": post.title,
            "description": post.description,
            "likes": post.likes,
            "dislikes": post.dislikes,
            "image": base64.b64encode(post.image).decode('utf-8') if post.image else None
        }
    }

@router.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    db.delete(post)
    db.commit()
    return {"message": "Post eliminado"}

# ---------- Endpoints para Comments ----------

@router.post("/posts/{post_id}/comments")
def create_comment(post_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    new_comment = Comment(
        post_id=post_id,
        user_id=comment.user_id,
        description=comment.description
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return {"message": "Comentario creado", "comment_id": new_comment.id}

@router.get("/posts/{post_id}/comments", response_model=List[dict])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    comments_data = [{
        "id": c.id,
        "post_id": c.post_id,
        "user": jsonable_encoder(c.user) if c.user else None,
        "created_at": c.created_at.isoformat(),
        "description": c.description,
        "likes": c.likes,
        "dislikes": c.dislikes
    } for c in comments]
    return comments_data

@router.put("/comments/{comment_id}")
def update_comment(comment_id: int, comment_update: CommentUpdate, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    if comment_update.description is not None:
        comment.description = comment_update.description
    db.commit()
    return {"message": "Comentario actualizado"}

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    db.delete(comment)
    db.commit()
    return {"message": "Comentario eliminado"}

@router.get("/posts/{post_id}/detalles")
def get_post_with_comments(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    comentarios = db.query(Comment).filter(Comment.post_id == post_id).all()

    post_data = {
        "id": post.id,
        "user_id": post.user_id,
        "created_at": post.created_at.isoformat(),
        "title": post.title,
        "description": post.description,
        "likes": post.likes,
        "dislikes": post.dislikes,
        "image": base64.b64encode(post.image).decode('utf-8') if post.image else None,
        "comments": [
            {
                "id": c.id,
                "user_id": c.user_id,
                "description": c.description,
                "created_at": c.created_at.isoformat(),
                "likes": c.likes,
                "dislikes": c.dislikes
            } for c in comentarios
        ]
    }

    return post_data

# ---------- Likes y Dislikes para Posts (News) ----------

@router.post("/posts/{post_id}/like")
def like_post(post_id: int, user_id: int = Form(...), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    # Verificar si ya dio like este usuario
    existing_like = db.query(NewsLike).filter(NewsLike.post_id == post_id, NewsLike.user_id == user_id).first()
    if existing_like:
        raise HTTPException(status_code=400, detail="Este usuario ya dio like a este post")
    nuevo_like = NewsLike(user_id=user_id, post_id=post_id)
    db.add(nuevo_like)
    post.likes += 1
    db.commit()
    return {"message": "Like registrado", "post_id": post_id, "user_id": user_id}

@router.post("/posts/{post_id}/dislike")
def dislike_post(post_id: int, user_id: int = Form(...), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    existing_dislike = db.query(NewsDislike).filter(NewsDislike.post_id == post_id, NewsDislike.user_id == user_id).first()
    if existing_dislike:
        raise HTTPException(status_code=400, detail="Este usuario ya dio dislike a este post")
    nuevo_dislike = NewsDislike(user_id=user_id, post_id=post_id)
    db.add(nuevo_dislike)
    post.dislikes += 1
    db.commit()
    return {"message": "Dislike registrado en post", "post_id": post_id, "user_id": user_id}

# ---------- Likes y Dislikes para Comments ----------

@router.post("/comments/{comment_id}/like")
def like_comment(comment_id: int, user_id: int = Form(...), db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    existing_like = db.query(CommentLike).filter(CommentLike.comment_id == comment_id, CommentLike.user_id == user_id).first()
    if existing_like:
        raise HTTPException(status_code=400, detail="Este usuario ya dió like a este comentario")
    nuevo_like = CommentLike(user_id=user_id, comment_id=comment_id)
    db.add(nuevo_like)
    comment.likes += 1
    db.commit()
    return {"message": "Like registrado en comentario", "comment_id": comment_id, "user_id": user_id}

@router.post("/comments/{comment_id}/dislike")
def dislike_comment(comment_id: int, user_id: int = Form(...), db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    existing_dislike = db.query(CommentDislike).filter(CommentDislike.comment_id == comment_id, CommentDislike.user_id == user_id).first()
    if existing_dislike:
        raise HTTPException(status_code=400, detail="Este usuario ya dió dislike a este comentario")
    nuevo_dislike = CommentDislike(user_id=user_id, comment_id=comment_id)
    db.add(nuevo_dislike)
    comment.dislikes += 1
    db.commit()
    return {"message": "Dislike registrado en comentario", "comment_id": comment_id, "user_id": user_id}

@router.get("/posts/{post_id}/likes", tags=["News"])
def get_post_likes(post_id: int, db: Session = Depends(get_db)):
    likes = db.query(NewsLike).filter(NewsLike.post_id == post_id).all()
    count = len(likes)
    # Se asume que la relación "user" está definida en el modelo NewsLike
    users = [jsonable_encoder(like.user) for like in likes]
    return {"post_id": post_id, "like_count": count, "users": users}

@router.get("/posts/{post_id}/dislikes", tags=["News"])
def get_post_dislikes(post_id: int, db: Session = Depends(get_db)):
    dislikes = db.query(NewsDislike).filter(NewsDislike.post_id == post_id).all()
    count = len(dislikes)
    users = [jsonable_encoder(dislike.user) for dislike in dislikes]
    return {"post_id": post_id, "dislike_count": count, "users": users}

@router.delete("/posts/{post_id}/like")
def remove_like(post_id: int, user_id: int = Form(...), db: Session = Depends(get_db)):
    like = db.query(NewsLike).filter(NewsLike.post_id == post_id, NewsLike.user_id == user_id).first()
    if not like:
        raise HTTPException(status_code=404, detail="Like no encontrado")
    db.delete(like)
    post = db.query(Post).filter(Post.id == post_id).first()
    if post and post.likes > 0:
        post.likes -= 1
    db.commit()
    return {"message": "Like removido", "post_id": post_id, "user_id": user_id}

# Remover like de un post (news)
@router.delete("/posts/{post_id}/like")
def remove_like_post(post_id: int, user_id: int = Form(...), db: Session = Depends(get_db)):
    like = db.query(NewsLike).filter(NewsLike.post_id == post_id, NewsLike.user_id == user_id).first()
    if not like:
        raise HTTPException(status_code=404, detail="Like no encontrado")
    db.delete(like)
    post = db.query(Post).filter(Post.id == post_id).first()
    if post and post.likes > 0:
        post.likes -= 1
    db.commit()
    return {"message": "Like retirado", "post_id": post_id, "user_id": user_id}

# Remover dislike de un post (news)
@router.delete("/posts/{post_id}/dislike")
def remove_dislike_post(post_id: int, user_id: int = Form(...), db: Session = Depends(get_db)):
    dislike = db.query(NewsDislike).filter(NewsDislike.post_id == post_id, NewsDislike.user_id == user_id).first()
    if not dislike:
        raise HTTPException(status_code=404, detail="Dislike no encontrado")
    db.delete(dislike)
    post = db.query(Post).filter(Post.id == post_id).first()
    if post and post.dislikes > 0:
        post.dislikes -= 1
    db.commit()
    return {"message": "Dislike retirado", "post_id": post_id, "user_id": user_id}

# Remover like de un comentario
@router.delete("/comments/{comment_id}/like")
def remove_like_comment(comment_id: int, user_id: int = Form(...), db: Session = Depends(get_db)):
    like = db.query(CommentLike).filter(CommentLike.comment_id == comment_id, CommentLike.user_id == user_id).first()
    if not like:
        raise HTTPException(status_code=404, detail="Like en comentario no encontrado")
    db.delete(like)
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment and comment.likes > 0:
        comment.likes -= 1
    db.commit()
    return {"message": "Like retirado del comentario", "comment_id": comment_id, "user_id": user_id}

# Remover dislike de un comentario
@router.delete("/comments/{comment_id}/dislike")
def remove_dislike_comment(comment_id: int, user_id: int = Form(...), db: Session = Depends(get_db)):
    dislike = db.query(CommentDislike).filter(CommentDislike.comment_id == comment_id, CommentDislike.user_id == user_id).first()
    if not dislike:
        raise HTTPException(status_code=404, detail="Dislike en comentario no encontrado")
    db.delete(dislike)
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment and comment.dislikes > 0:
        comment.dislikes -= 1
    db.commit()
    return {"message": "Dislike retirado del comentario", "comment_id": comment_id, "user_id": user_id}