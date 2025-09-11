from typing import List, Optional, Tuple
from sqlmodel import select, Session, func
from app.models.comment import Comment

class CommentRepo:
    def __init__(self, session: Session):
        self.session = session

    def create(self, comment: Comment) -> Comment:
        self.session.add(comment)
        self.session.commit()
        self.session.refresh(comment)
        return comment
    
    def get_all(self, limit: int, offset: int) -> Tuple[List[Comment], int]:
        query = select(Comment).order_by(Comment.created_at.desc())
        total = self.session.exec(select(func.count()).select_from(query.subquery())).one()
        comments = self.session.exec(query.offset(offset).limit(limit)).all()
        return comments, total
    
    def get_by_video_id(self, video_id: str, limit: int, offset: int) -> Tuple[List[Comment], int]:
        query = select(Comment).where(Comment.video_id == video_id).order_by(Comment.created_at.desc())
        total = self.session.exec(select(func.count()).select_from(query.subquery())).one()
        comments = self.session.exec(query.offset(offset).limit(limit)).all()
        return comments, total
    
    def update_by_id(self, comment_id: str, **kwargs) -> Optional[Comment]:
        comment = self.get(comment_id)
        if not comment:
            return None
        for key, value in kwargs.items():
            setattr(comment, key, value)
        self.session.add(comment)
        self.session.commit()
        self.session.refresh(comment)
        return comment
    
    def delete_by_video_id(self, video_id: str) -> int:
        query = select(Comment).where(Comment.video_id == video_id)
        comments = self.session.exec(query).all()
        count = len(comments)
        for comment in comments:
            self.session.delete(comment)
        self.session.commit()
        return count
    
    def list_replies(self, parent_id: str, limit: int, offset: int) -> Tuple[List[Comment], int]:
        query = select(Comment).where(Comment.parent_id == parent_id).order_by(Comment.created_at.desc())
        total = self.session.exec(select(func.count()).select_from(query.subquery())).one()
        comments = self.session.exec(query.offset(offset).limit(limit)).all()
        return comments, total
    
    def increment_like(self, comment_id: str, delta: int = 1) -> Optional[Comment]:
        comment = self.get(comment_id)
        if not comment:
            return None
        comment.like_count += delta
        self.session.add(comment)
        self.session.commit()
        self.session.refresh(comment)
        return comment