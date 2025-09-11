from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from app.schemes.comment import CommentCreate, CommentRead, CommentList, CommentUpdate, CommentDelete
from app.api.dependencies import get_current_user  # JWT dependency (returns payload dict)
from app.services import comment_service
from app.models.comment import Comment as CommentModel

router = APIRouter()

@router.post("/", response_model=CommentRead, status_code=201)
async def create_comment(payload: CommentCreate, current=Depends(get_current_user)):
    """
    Create a comment. `get_current_user` should return a payload dict with "sub" or "user_id".
    """
    # extract user id from token payload (support both 'sub' and 'user_id')
    user_id = None
    if isinstance(current, dict):
        user_id = str(current.get("sub") or current.get("user_id") or current.get("id"))
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication payload")

    created = await comment_service.create_comment(user_id, payload)
    return created

@router.get("/video/{video_id}", response_model=CommentList, status_code=status.HTTP_200_OK)
async def get_comments(video_id: str, limit: int = Query(20, ge=1, le=200), offset: int = Query(0, ge=0)):
    items, total = await comment_service.list_comments(video_id=video_id, limit=limit, offset=offset)
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.get("/replies/{parent_id}", response_model=List[CommentRead], status_code=status.HTTP_200_OK)
async def get_replies(parent_id: str):
    replies = await comment_service.list_replies(parent_id)
    return replies

@router.get("/{comment_id}", response_model=CommentRead, status_code=status.HTTP_200_OK)
async def get_comment(comment_id: str):
    c = await comment_service.get_comment(comment_id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return c

@router.delete("/{comment_id}", status_code=status.HTTP_200_OK)
async def delete_comment(comment_id: str, current=Depends(get_current_user)):
    user_id = None
    if isinstance(current, dict):
        user_id = str(current.get("sub") or current.get("user_id") or current.get("id"))
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication payload")
    try:
        ok = await comment_service.delete_comment(user_id, comment_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return {"status": "deleted"}