# app/services/auth_service.py
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.token import Token
from app.utils.security import (
    create_access_token, create_refresh_token,
    decode_refresh_token, decode_access_token, hash_token
)
import os

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def issue_tokens(self, user_id: str):
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        access_hash = hash_token(access_token)
        refresh_hash = hash_token(refresh_token)

        access_exp = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv("JWT_ACCESS_EXPIRATION", "15")))
        refresh_exp = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv("JWT_REFRESH_EXPIRATION", "10080")))

        self.db.add(Token(user_id=user_id, token_hash=access_hash, token_type="access", expires_at=access_exp))
        self.db.add(Token(user_id=user_id, token_hash=refresh_hash, token_type="refresh", expires_at=refresh_exp))
        self.db.commit()
        return access_token, refresh_token

    def refresh_tokens(self, refresh_token_raw: str):
        payload = decode_refresh_token(refresh_token_raw)
        if not payload:
            return None
        user_id = payload["sub"]
        token_hash = hash_token(refresh_token_raw)
        token_entry = self.db.query(Token).filter(
            Token.token_hash == token_hash,
            Token.token_type == "refresh",
            Token.revoked == False
        ).first()
        if not token_entry or token_entry.expires_at < datetime.now(timezone.utc):
            return None
        token_entry.revoked = True
        self.db.commit()
        return self.issue_tokens(user_id)

    def revoke_all_user_tokens(self, user_id: str):
        self.db.query(Token).filter(
            Token.user_id == user_id,
            Token.revoked == False
        ).update({"revoked": True})
        self.db.commit()

    def revoke_specific_token(self, token_raw: str, token_type: str):
        token_hash = hash_token(token_raw)
        self.db.query(Token).filter(
            Token.token_hash == token_hash,
            Token.token_type == token_type
        ).update({"revoked": True})
        self.db.commit()

    def is_token_valid(self, token_raw: str, token_type: str) -> bool:
        payload = decode_access_token(token_raw) if token_type == "access" else decode_refresh_token(token_raw)
        if not payload:
            return False
        token_hash = hash_token(token_raw)
        entry = self.db.query(Token).filter(
            Token.token_hash == token_hash,
            Token.token_type == token_type,
            Token.revoked == False
        ).first()
        if entry and entry.expires_at > datetime.now(timezone.utc):
            return True
        return False