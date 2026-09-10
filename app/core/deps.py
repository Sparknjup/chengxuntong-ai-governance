"""
依赖注入 - 当前用户、权限检查等
"""
from fastapi import Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.models.user import User
from app.models.admin import Admin


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录的市民用户"""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("未提供有效的认证Token")

    token = authorization.split(" ")[1]
    payload = decode_access_token(token)

    if not payload or payload.get("type") != "user":
        raise UnauthorizedException("Token 无效或已过期")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id), User.is_deleted == False).first()

    if not user:
        raise UnauthorizedException("用户不存在")
    if user.status != "正常":
        raise ForbiddenException(f"账号状态异常：{user.status}")

    return user


def get_current_admin(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Admin:
    """获取当前登录的管理员"""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("未提供有效的认证Token")

    token = authorization.split(" ")[1]
    payload = decode_access_token(token)

    if not payload or payload.get("type") != "admin":
        raise UnauthorizedException("Token 无效或已过期")

    admin_id = payload.get("sub")
    admin = db.query(Admin).filter(Admin.id == int(admin_id), Admin.is_deleted == False).first()

    if not admin:
        raise UnauthorizedException("管理员不存在")

    return admin


def require_super_admin(admin: Admin = Depends(get_current_admin)) -> Admin:
    """要求超级管理员权限"""
    if admin.role != "超级管理员":
        raise ForbiddenException("需要超级管理员权限")
    return admin
