"""
用户 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.common import success
from app.schemas.user import (
    UserRegister, UserLogin, UserUpdate, PasswordChange,
    UserInfo, TokenResponse,
)
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", summary="市民注册")
def register(data: UserRegister, db: Session = Depends(get_db)):
    user = UserService.register(db, data)
    return success(
        data={"user_id": user.id, "name": user.name},
        message="注册成功"
    )


@router.post("/login", summary="市民登录", response_model=None)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user, token = UserService.login(db, data.phone, data.password)
    return success(data={
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name,
        "points": user.points,
        "level": user.level,
    }, message="登录成功")


@router.get("/me", summary="获取当前用户信息")
def get_me(current_user: User = Depends(get_current_user)):
    return success(data=UserInfo.model_validate(current_user).model_dump(mode="json"))


@router.put("/me", summary="更新当前用户信息")
def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if data.name is not None:
        current_user.name = data.name
    if data.avatar is not None:
        current_user.avatar = data.avatar
    db.commit()
    db.refresh(current_user)
    return success(data=UserInfo.model_validate(current_user).model_dump(mode="json"))


@router.post("/change-password", summary="修改密码")
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    UserService.change_password(db, current_user, data.old_password, data.new_password)
    return success(message="密码修改成功")
