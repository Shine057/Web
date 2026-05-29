from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.user import UserCreate, UserLogin, ForgotPassword, ResetPassword, UserResponse
from app.schemas.auth import Message
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.dependencies import get_current_user
from app.utils.security import decode_access_token
from fastapi.responses import RedirectResponse
import httpx
import os
import uuid

router = APIRouter(prefix="/auth", tags=["Auth"])

def set_cookies(response: Response, access_token: str, refresh_token: str):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,   # для локальной разработки
        max_age=int(os.getenv("JWT_ACCESS_EXPIRATION", "15")) * 60
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=int(os.getenv("JWT_REFRESH_EXPIRATION", "10080")) * 60
    )

# ---------- Регистрация ----------
@router.post("/register",
             response_model=UserResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Регистрация нового пользователя",
             tags=["Auth"],
             responses={
                 201: {"description": "Пользователь успешно создан"},
                 400: {"description": "Некорректные данные или пользователь уже существует"}
             })
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    try:
        user = user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# ---------- Вход ----------
@router.post("/login",
             response_model=Message,
             summary="Вход в систему (установка HttpOnly cookies)",
             tags=["Auth"],
             responses={
                 200: {"description": "Успешный вход, куки установлены"},
                 401: {"description": "Неверные учетные данные"}
             })
def login(credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.verify_credentials(credentials.login, credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    auth_service = AuthService(db)
    access_token, refresh_token = auth_service.issue_tokens(str(user.id))
    set_cookies(response, access_token, refresh_token)
    return {"detail": "Logged in"}

# ---------- Обновление токенов ----------
@router.post("/refresh",
             response_model=Message,
             summary="Обновление Access и Refresh токенов",
             tags=["Auth"],
             responses={
                 200: {"description": "Токены успешно обновлены"},
                 401: {"description": "Невалидный или просроченный refresh token"}
             })
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")
    auth_service = AuthService(db)
    result = auth_service.refresh_tokens(refresh_token)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    new_access, new_refresh = result
    set_cookies(response, new_access, new_refresh)
    return {"detail": "Tokens refreshed"}

# ---------- Проверка статуса ----------
@router.get("/whoami",
            response_model=UserResponse,
            summary="Информация о текущем пользователе",
            tags=["Auth"],
            responses={
                200: {"description": "Данные профиля"},
                401: {"description": "Не авторизован"}
            })
def whoami(current_user = Depends(get_current_user)):
    return current_user

# ---------- Выход (текущая сессия) ----------
@router.post("/logout",
             response_model=Message,
             summary="Завершение текущей сессии (отзыв токенов)",
             tags=["Auth"],
             responses={
                 200: {"description": "Сессия завершена, куки удалены"}
             })
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    access_token = request.cookies.get("access_token")
    if access_token:
        auth_service.revoke_specific_token(access_token, "access")
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        auth_service.revoke_specific_token(refresh_token, "refresh")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "Logged out"}

# ---------- Выход (все сессии) ----------
@router.post("/logout-all",
             response_model=Message,
             summary="Завершение всех сессий пользователя",
             tags=["Auth"],
             responses={
                 200: {"description": "Все сессии завершены"}
             })
def logout_all(request: Request, response: Response, current_user = Depends(get_current_user),
               db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    auth_service.revoke_all_user_tokens(str(current_user.id))
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "All sessions terminated"}

# ------------------ OAuth Яндекс ------------------
@router.get("/oauth/yandex",
            summary="Вход через Яндекс (редирект на провайдера)",
            tags=["OAuth"],
            response_class=RedirectResponse,
            responses={
                302: {"description": "Перенаправление на страницу авторизации Яндекса"}
            })
async def oauth_yandex(request: Request):
    state = str(uuid.uuid4())
    redirect_uri = os.getenv("YANDEX_REDIRECT_URI")
    client_id = os.getenv("YANDEX_CLIENT_ID")
    auth_url = (
        f"https://oauth.yandex.ru/authorize?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
    )
    response = RedirectResponse(auth_url)
    response.set_cookie(key="oauth_state", value=state, httponly=True, samesite="lax", max_age=300)
    return response

@router.get("/oauth/yandex/callback",
            summary="Callback OAuth Яндекса (завершение входа)",
            tags=["OAuth"],
            response_class=RedirectResponse,
            responses={
                302: {"description": "Перенаправление на главную страницу с установленными куками"},
                400: {"description": "Ошибка проверки state или обмена токена"}
            })
async def oauth_yandex_callback(request: Request, code: str = Query(...), state: str = Query(...),
                                db: Session = Depends(get_db)):
    saved_state = request.cookies.get("oauth_state")
    if not saved_state or saved_state != state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state")
    # Обмен кода на токен
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth.yandex.ru/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": os.getenv("YANDEX_CLIENT_ID"),
                "client_secret": os.getenv("YANDEX_CLIENT_SECRET"),
                "redirect_uri": os.getenv("YANDEX_REDIRECT_URI")
            }
        )
        if token_response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token exchange failed")
        token_data = token_response.json()
        access_token = token_data["access_token"]

        # Запрос данных пользователя
        user_response = await client.get(
            "https://login.yandex.ru/info?format=json",
            headers={"Authorization": f"OAuth {access_token}"}
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get user info")
        user_info = user_response.json()
        yandex_id = user_info["id"]
        email = user_info.get("default_email")

    # Локальный пользователь
    user_service = UserService(db)
    user = user_service.create_or_get_oauth_user("yandex", yandex_id, email=email)

    # Генерация локальных токенов
    auth_service = AuthService(db)
    access, refresh = auth_service.issue_tokens(str(user.id))
    response = RedirectResponse(url="http://localhost:4200/")
    set_cookies(response, access, refresh)
    response.delete_cookie("oauth_state")
    return response

# ------------------ Заглушки forgot/reset password ------------------
@router.post("/forgot-password",
             response_model=Message,
             summary="Запрос на восстановление пароля (заглушка)",
             tags=["Auth"],
             responses={
                 200: {"description": "Если email существует, ссылка отправлена"}
             })
def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    return {"detail": "If the email exists, a reset link has been sent"}

@router.post("/reset-password",
             response_model=Message,
             summary="Сброс пароля (заглушка)",
             tags=["Auth"],
             responses={
                 501: {"description": "Не реализовано"}
             })
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")