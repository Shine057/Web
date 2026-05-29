from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.user_service import UserService
from app.services.auth_service import AuthService

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    auth_service = AuthService(db)
    if not auth_service.is_token_valid(token, "access"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    from app.utils.security import decode_access_token
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    user_service = UserService(db)
    user = user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user