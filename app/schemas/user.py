"""
用户数据校验
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class UserRegister(BaseModel):
    """注册请求"""
    name: str = Field(min_length=2, max_length=50, description="姓名")
    phone: str = Field(description="手机号")
    password: str = Field(min_length=6, max_length=50, description="密码")
    id_card: Optional[str] = Field(None, description="身份证号")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v

    @field_validator("id_card")
    @classmethod
    def validate_id_card(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^\d{17}[\dXx]$", v):
            raise ValueError("身份证号格式不正确")
        return v


class UserLogin(BaseModel):
    """登录请求"""
    phone: str
    password: str


class TokenResponse(BaseModel):
    """登录返回"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    points: int
    level: str


class UserInfo(BaseModel):
    """用户信息"""
    id: int
    name: str
    phone: str
    avatar: Optional[str] = None
    points: int
    level: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """更新用户信息"""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    avatar: Optional[str] = None


class PasswordChange(BaseModel):
    """修改密码"""
    old_password: str
    new_password: str = Field(min_length=6, max_length=50)
