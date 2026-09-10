"""
用户业务逻辑
"""
from datetime import timedelta
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logger import logger
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import (
    ConflictException, UnauthorizedException, ForbiddenException, NotFoundException
)
from app.models import User
from app.schemas.user import UserRegister


class UserService:

    @staticmethod
    def register(db: Session, data: UserRegister) -> User:
        """市民注册"""
        existed = db.query(User).filter(User.phone == data.phone).first()
        if existed:
            raise ConflictException("该手机号已注册")

        user = User(
            name=data.name,
            phone=data.phone,
            password=hash_password(data.password),
            id_card=data.id_card,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"用户注册成功 phone={data.phone} user_id={user.id}")
        return user

    @staticmethod
    def login(db: Session, phone: str, password: str) -> tuple[User, str]:
        """市民登录，返回 (user, token)"""
        user = db.query(User).filter(User.phone == phone, User.is_deleted == False).first()
        if not user:
            raise UnauthorizedException("手机号或密码错误")

        if not verify_password(password, user.password):
            raise UnauthorizedException("手机号或密码错误")

        if user.status != "正常":
            raise ForbiddenException(f"账号状态：{user.status}")

        token = create_access_token(
            data={"sub": str(user.id), "type": "user"},
            expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
        )
        logger.info(f"用户登录成功 user_id={user.id}")
        return user, token

    @staticmethod
    def change_password(db: Session, user: User, old_password: str, new_password: str):
        """修改密码"""
        if not verify_password(old_password, user.password):
            raise UnauthorizedException("旧密码错误")
        user.password = hash_password(new_password)
        db.commit()
        logger.info(f"用户修改密码 user_id={user.id}")
