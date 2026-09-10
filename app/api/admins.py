"""
管理员 API
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_admin, require_super_admin
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import (
    ConflictException, UnauthorizedException, NotFoundException
)
from app.core.logger import logger
from app.models import Admin, User
from app.schemas.common import success
from app.schemas.__init__ import AdminCreate, AdminLogin, AdminInfo

router = APIRouter()


@router.post("/login", summary="管理员登录")
def login(data: AdminLogin, request: Request, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(
        Admin.username == data.username, Admin.is_deleted == False
    ).first()
    if not admin or not verify_password(data.password, admin.password):
        raise UnauthorizedException("用户名或密码错误")

    # 记录登录信息
    admin.last_login_at = datetime.now()
    admin.last_login_ip = request.client.host if request.client else None
    db.commit()

    token = create_access_token(
        data={"sub": str(admin.id), "type": "admin"},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    )
    logger.info(f"管理员登录 username={admin.username}")

    return success(data={
        "access_token": token,
        "token_type": "bearer",
        "admin_id": admin.id,
        "username": admin.username,
        "role": admin.role,
        "department_id": admin.department_id,
    }, message="登录成功")


@router.get("/me", summary="当前管理员信息")
def get_me(admin: Admin = Depends(get_current_admin)):
    return success(data=AdminInfo.model_validate(admin).model_dump(mode="json"))


@router.post("/create", summary="创建管理员（仅超管）")
def create_admin(
    data: AdminCreate,
    super_admin: Admin = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    if db.query(Admin).filter(Admin.username == data.username).first():
        raise ConflictException("用户名已存在")

    admin = Admin(
        username=data.username,
        password=hash_password(data.password),
        real_name=data.real_name,
        role=data.role,
        department_id=data.department_id,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    logger.info(f"管理员创建 username={admin.username} by={super_admin.username}")
    return success(data=AdminInfo.model_validate(admin).model_dump(mode="json"), message="管理员创建成功")


# ========== 用户管理（管理员视角）==========
@router.get("/users", summary="所有市民用户列表（管理员）")
def list_users(
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(User).filter(User.is_deleted == False)
    if status:
        query = query.filter(User.status == status)
    if keyword:
        query = query.filter(
            (User.name.contains(keyword)) | (User.phone.contains(keyword))
        )

    total = query.count()
    users = query.order_by(User.created_at.desc())\
                 .offset((page - 1) * page_size).limit(page_size).all()

    return success(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": u.id,
                "name": u.name,
                "phone": u.phone,
                "points": u.points,
                "level": u.level,
                "status": u.status,
                "created_at": u.created_at,
            }
            for u in users
        ]
    })


@router.put("/users/{user_id}/status", summary="冻结/解冻用户（仅超管）")
def update_user_status(
    user_id: int,
    status: str = Query(..., description="正常 / 冻结"),
    admin: Admin = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    if status not in ("正常", "冻结"):
        raise ConflictException("status 必须是 正常 或 冻结")

    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise NotFoundException("用户不存在")
    user.status = status
    db.commit()
    logger.info(f"用户状态变更 user_id={user_id} status={status} by={admin.username}")
    return success(message=f"用户状态已更新为：{status}")
