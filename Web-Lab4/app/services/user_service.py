# app/services/user_service.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import hash_password, verify_password

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str):
        return self.db.query(User).filter(User.id == user_id, User.is_deleted == False).first()

    def get_by_login(self, login: str):
        """Ищет пользователя по email или телефону."""
        return self.db.query(User).filter(
            (User.email == login) | (User.phone == login),
            User.is_deleted == False
        ).first()

    def get_by_yandex_id(self, yid: str):
        return self.db.query(User).filter(User.yandex_id == yid, User.is_deleted == False).first()

    def get_by_vk_id(self, vid: str):
        return self.db.query(User).filter(User.vk_id == vid, User.is_deleted == False).first()

    def create_user(self, data: UserCreate):
        if data.email:
            existing = self.db.query(User).filter(User.email == data.email).first()
            if existing:
                raise ValueError("Email already exists")
        if data.phone:
            existing = self.db.query(User).filter(User.phone == data.phone).first()
            if existing:
                raise ValueError("Phone already exists")
        hashed = hash_password(data.password)
        user = User(
            email=data.email,
            phone=data.phone,
            hashed_password=hashed
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def verify_credentials(self, login: str, password: str):
        user = self.get_by_login(login)
        if not user or not user.hashed_password:
            return None
        if verify_password(password, user.hashed_password):
            return user
        return None

    def create_or_get_oauth_user(self, provider: str, provider_id: str, email: str = None, phone: str = None):
        if provider == "yandex":
            user = self.get_by_yandex_id(provider_id)
            if user:
                return user
            user = User(yandex_id=provider_id, email=email)
        elif provider == "vk":
            user = self.get_by_vk_id(provider_id)
            if user:
                return user
            user = User(vk_id=provider_id, phone=phone)
        else:
            raise ValueError("Unsupported provider")
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user_id: str, new_password: str):
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        user.hashed_password = hash_password(new_password)
        self.db.commit()