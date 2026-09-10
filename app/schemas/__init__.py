"""
其他数据校验
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ========== 部门 ==========
class DepartmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    code: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None


class DepartmentInfo(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ========== 管理员 ==========
class AdminCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=50)
    real_name: Optional[str] = None
    role: str = Field(default="部门管理员")
    department_id: Optional[int] = None


class AdminLogin(BaseModel):
    username: str
    password: str


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_id: int
    username: str
    role: str
    department_id: Optional[int]


class AdminInfo(BaseModel):
    id: int
    username: str
    real_name: Optional[str]
    role: str
    department_id: Optional[int]
    last_login_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


# ========== 积分 ==========
class PointsRecordInfo(BaseModel):
    id: int
    points: int
    points_after: int
    reason: str
    order_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


class RankingItem(BaseModel):
    rank: int
    user_id: int
    name: str
    points: int
    level: str


# ========== 统计 ==========
class OverviewStats(BaseModel):
    total_orders: int
    pending: int
    processing: int
    closed: int
    urgent: int
    total_users: int
    close_rate: str
    avg_rating: float
