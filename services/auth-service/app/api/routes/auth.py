from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.token import TokenSchema
from app.schemas.user import UserLogin, UserCreate
from app.services.auth_service import AuthService
from app.api.routes.dependencies import get_current_user

router = APIRouter()
auth_service = AuthService()

@router.post("/register", response_model=TokenSchema)
async def register(user: UserCreate):
    return await auth_service.register_user(user)

@router.post("/login", response_model=TokenSchema)
async def login(user: UserLogin):
    token = await auth_service.authenticate_user(user)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return token

@router.post("/logout")
async def logout(token: str = Depends(get_current_user)):
    await auth_service.logout(token)
    return {"status": "logged out"}
