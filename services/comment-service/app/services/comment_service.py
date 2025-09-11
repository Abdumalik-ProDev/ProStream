from typing import Tuple, List, Optional
from datetime import datetime
from sqlmodel import Session, select
from app.models.comment import Comment
from app.schemes.comment import CommentCreate
from app.repositories.comment_repo import CommentRepo as CommentRepository
import asyncio
from fastapi.concurrency import run_in_threadpool
from app.core.config import settings
from app.utils.kafka import send_event  # send_event(topic, key, value)

# NOTE: This file uses sync DB operations (sqlmodel 0.0.8). We run them in a threadpool.

def _create_comment_sync(session: Session, user_id: str, payload: CommentCreate) -> Comment:
    repo = CommentRepository(session)
    comment = Comment(
        user_id=user_id,
        video_id=payload.video_id,
        parent_id=payload.parent_id,
        content=payload.content,
        created_at=datetime.utcnow(),
    )
    return repo.create(comment)

async def create_comment(user_id: str, payload: CommentCreate) -> Comment:
    """
    Create a comment in a threadpool so FastAPI remains async.
    Publishes a Kafka event after creation.
    """
    # obtain a new session per operation
    from app.core.db import SessionLocal  # import inside function to avoid circular imports

    def _sync():
        s = SessionLocal()
        try:
            return _create_comment_sync(s, user_id, payload)
        finally:
            s.close()

    saved: Comment = await run_in_threadpool(_sync)

    # publish kafka event (non-blocking)
    try:
        loop = asyncio.get_running_loop()
        await send_event(settings.kafka_topic, saved.id, {"event": "comment.created", "comment_id": saved.id, "video_id": saved.video_id, "user_id": saved.user_id})
    except Exception:
        # don't fail the request if kafka is down; log quietly
        pass

    return saved

def _get_comment_sync(session: Session, comment_id: str) -> Optional[Comment]:
    repo = CommentRepository(session)
    return repo.get(comment_id)

async def get_comment(comment_id: str) -> Optional[Comment]:
    from app.core.db import SessionLocal

    def _sync():
        s = SessionLocal()
        try:
            return _get_comment_sync(s, comment_id)
        finally:
            s.close()

    return await run_in_threadpool(_sync)

def _list_comments_sync(session: Session, video_id: str, limit: int, offset: int) -> Tuple[List[Comment], int]:
    repo = CommentRepository(session)
    return repo.list_by_video(video_id=video_id, limit=limit, offset=offset)

async def list_comments(video_id: str, limit: int = 20, offset: int = 0) -> Tuple[List[Comment], int]:
    from app.core.db import SessionLocal

    def _sync():
        s = SessionLocal()
        try:
            return _list_comments_sync(s, video_id, limit, offset)
        finally:
            s.close()

    return await run_in_threadpool(_sync)

def _list_replies_sync(session: Session, parent_id: str):
    repo = CommentRepository(session)
    return repo.list_replies(parent_id)

async def list_replies(parent_id: str):
    from app.core.db import SessionLocal

    def _sync():
        s = SessionLocal()
        try:
            return _list_replies_sync(s, parent_id)
        finally:
            s.close()

    return await run_in_threadpool(_sync)

def _delete_comment_sync(session: Session, user_id: str, comment_id: str) -> Tuple[bool, Optional[str]]:
    repo = CommentRepository(session)
    c = repo.get(comment_id)
    if not c:
        return False, "not_found"
    if c.user_id != user_id:
        return False, "forbidden"
    ok = repo.soft_delete(comment_id)
    return ok, None

async def delete_comment(user_id: str, comment_id: str) -> bool:
    from app.core.db import SessionLocal

    def _sync():
        s = SessionLocal()
        try:
            return _delete_comment_sync(s, user_id, comment_id)
        finally:
            s.close()

    ok, err = await run_in_threadpool(_sync)
    if ok:
        # fire deletion event
        try:
            await send_event(settings.kafka_topic, comment_id, {"event": "comment.deleted", "comment_id": comment_id})
        except Exception:
            pass
        return True
    if err == "forbidden":
        raise PermissionError("not allowed")
    return False