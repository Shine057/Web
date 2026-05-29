import os
import bcrypt
import jwt
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

ACCESS_SECRET = os.getenv("JWT_ACCESS_SECRET", "fallback-access")
REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET", "fallback-refresh")
ACCESS_EXP_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRATION", "15"))
REFRESH_EXP_MINUTES = int(os.getenv("JWT_REFRESH_EXPIRATION", "10080"))
TOKEN_HASH_SALT = os.getenv("TOKEN_HASH_SALT", "default-salt")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def hash_token(token: str) -> str:
    """Детерминированный хеш для поиска токена в БД."""
    return hashlib.sha256((token + TOKEN_HASH_SALT).encode()).hexdigest()

def create_access_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_EXP_MINUTES),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, ACCESS_SECRET, algorithm="HS256")

def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=REFRESH_EXP_MINUTES),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, REFRESH_SECRET, algorithm="HS256")

def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, ACCESS_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None

def decode_refresh_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, REFRESH_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None