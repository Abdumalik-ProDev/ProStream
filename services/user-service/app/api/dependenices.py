from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.security.jwt import verify_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_jwt(token)
    if not payload:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload