from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import AsyncSessionLocal
from app.api.dependenices import get_current_user
from app.schemes.profile import ProfileCreate, ProfileRead, ProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/users", tags=["users"])

async def get_session() -> AsyncSession: # pyright: ignore[reportInvalidTypeForm]
    async with AsyncSessionLocal() as s:
        yield s

@router.post("/", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(payload: ProfileCreate, session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    svc = ProfileService(session)
    try:
        prof = await svc.create_profile(payload)
        return prof
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.get("/me", response_class=ProfileRead, status_code=status.HTTP_200_OK)
async def read_my_profile_by_id(session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    user_id = int(current.get("sub"))
    svc = ProfileService(session)
    prof = await svc.get_profile_by_user_id(user_id)
    if not prof:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return prof

@router.get("/me", response_class=ProfileRead, status_code=status.HTTP_200_OK)
async def read_my_profile_by_username(session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    username = str(current.get())
    svc = ProfileService(session)
    prof = await svc.get_profile_by_username(username)
    if not prof:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return prof

@router.patch("/me", response_model=ProfileRead, status_code=status.HTTP_200_OK)
async def update_profile(payload: ProfileUpdate, session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    user_id = int(current.get("sub"))
    username = str(current.get())
    svc = ProfileService(session)
    try:
        prof = await svc.update_profile(user_id, username, payload)
        return prof
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile not found")