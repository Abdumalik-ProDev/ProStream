from typing import List, Optional, Tuple
from sqlmodel import Session
from fastapi.concurrency import run_in_threadpool
from app.models.comment import Comment
from app.schemes.comment import CommentCreate, CommentRead, CommentUpdate, CommentDelete, CommentList
from app.repositories.comment_repo import CommentRepo
from app.core.db import SessionLocal
from app.utils.kafka import kafka_producer
from app.core.config import settings
from datetime import datetime
import asyncio

def _create_repo() -> CommentRepo:
    session = SessionLocal()
    return CommentRepo(session)

async def create_comment(user_id: str, payload: CommentCreate) -> CommentRead:
    repo = _create_repo()
    comment = Comment(
        user_id=user_id,
        video_id=payload.video_id,
        parent_id=payload.parent_id,
        content=payload.content,
        is_deleted=False,
        is_hidden=False,
        like_count=0,
        created_at=datetime.utcnow(),
        updated_at=None
    )
    created_comment = await run_in_threadpool(repo.create, comment)
    asyncio.create_task(kafka_producer.send_and_wait(
        topic=settings.KAFKA_TOPIC_COMMENTS,
        key=str(created_comment.id).encode('utf-8'),
        value={
            "action": "create",
            "comment": created_comment.dict()
        }
    ))
    return CommentRead.from_orm(created_comment)

async def get_comments(limit: int = 10, offset: int = 0) -> CommentList:
    repo = _create_repo()
    comments, total = await run_in_threadpool(repo.get_all, limit, offset)
    return CommentList(
        items=[CommentRead.from_orm(c) for c in comments],
        total=total,
        limit=limit,
        offset=offset
    )

async def get_comments_by_video(video_id: str, limit: int = 10, offset: int = 0) -> CommentList:
    repo = _create_repo()
    comments, total = await run_in_threadpool(repo.get_by_video_id, video_id, limit, offset)
    return CommentList(
        items=[CommentRead.from_orm(c) for c in comments],
        total=total,
        limit=limit,
        offset=offset
    )

async def update_comment(comment_id: str, payload: CommentUpdate) -> Optional[CommentRead]:
    repo = _create_repo()
    update_data = payload.dict(exclude_unset=True)
    if update_data:
        update_data['updated_at'] = datetime.utcnow()
    updated_comment = await run_in_threadpool(repo.update_by_id, comment_id, **update_data)
    if updated_comment:
        asyncio.create_task(kafka_producer.send_and_wait(
            topic=settings.KAFKA_TOPIC_COMMENTS,
            key=str(updated_comment.id).encode('utf-8'),
            value={
                "action": "update",
                "comment": updated_comment.dict()
            }
        ))
        return CommentRead.from_orm(updated_comment)
    return None

async def delete_comments_by_video(video_id: str) -> CommentDelete:
    repo = _create_repo()
    deleted_count = await run_in_threadpool(repo.delete_by_video_id, video_id)
    asyncio.create_task(kafka_producer.send_and_wait(
        topic=settings.KAFKA_TOPIC_COMMENTS,
        key=video_id.encode('utf-8'),
        value={
            "action": "delete_by_video",
            "video_id": video_id,
            "deleted_count": deleted_count
        }
    ))
    return CommentDelete(id=video_id, is_deleted=True)

async def list_replies(parent_id: str, limit: int = 10, offset: int = 0) -> CommentList:
    repo = _create_repo()
    comments, total = await run_in_threadpool(repo.list_replies, parent_id, limit, offset)
    return CommentList(
        items=[CommentRead.from_orm(c) for c in comments],
        total=total,
        limit=limit,
        offset=offset
    )

async def increment_like(comment_id: str, delta: int = 1) -> Optional[CommentRead]:
    repo = _create_repo()
    updated_comment = await run_in_threadpool(repo.increment_like, comment_id, delta)
    if updated_comment:
        asyncio.create_task(kafka_producer.send_and_wait(
            topic=settings.KAFKA_TOPIC_COMMENTS,
            key=str(updated_comment.id).encode('utf-8'),
            value={
                "action": "increment_like",
                "comment": updated_comment.dict()
            }
        ))
        return CommentRead.from_orm(updated_comment)
    return None