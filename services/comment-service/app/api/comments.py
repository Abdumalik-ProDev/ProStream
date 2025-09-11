from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemes.comment import CommentCreate, CommentRead, CommentList, CommentUpdate, CommentDelete
from app.services import comment_service
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/comment", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(
    payload: CommentCreate,
    current_user: dict = Depends(get_current_user)
):
    return await comment_service.create_comment(current_user["sub"], payload)

@router.get("/comments", response_model=CommentList, status_code=status.HTTP_200_OK)
async def get_comments(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return await comment_service.get_comments(limit, offset)

@router.get("/video/{video_id}", response_model=CommentList, status_code=status.HTTP_200_OK)
async def get_comments_by_video(
    video_id: str,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return await comment_service.get_comments_by_video(video_id, limit, offset)

@router.put("/{comment_id}", response_model=CommentRead, status_code=status.HTTP_200_OK)
async def update_comment(
    comment_id: str,
    payload: CommentUpdate,
    current_user: dict = Depends(get_current_user)
):
    updated_comment = await comment_service.update_comment(comment_id, payload)
    if not updated_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return updated_comment

@router.delete("/{comment_id}", response_model=CommentRead, status_code=status.HTTP_200_OK)
async def delete_comment(
    comment_id: str,
    current_user: dict = Depends(get_current_user)
):
    deleted_comment = await comment_service.delete_comment(comment_id)
    if not deleted_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return deleted_comment

@router.get("/replies/{parent_id}", response_model=CommentList, status_code=status.HTTP_200_OK)
async def list_replies(
    parent_id: str,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return await comment_service.list_replies(parent_id, limit, offset)