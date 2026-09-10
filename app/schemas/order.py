"""
工单数据校验
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    """创建工单（表单参数，不通过此 schema 直接传，给文档参考）"""
    location: str = Field(description="位置信息")
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    text: Optional[str] = Field(None, description="文字描述（可选）")


class OrderBrief(BaseModel):
    """工单简要信息"""
    id: int
    order_no: str
    problem_type: str
    department_name: Optional[str] = None
    location: str
    urgency: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderDetail(BaseModel):
    """工单详情"""
    id: int
    order_no: str
    user_id: int
    user_name: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None

    problem_type: str
    multi_department: bool
    confidence: Optional[str] = None
    description: str
    audio_description: Optional[str] = None
    source: str

    image_path: Optional[str] = None
    audio_path: Optional[str] = None
    video_path: Optional[str] = None

    location: str
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    urgency: str
    status: str

    handler_name: Optional[str] = None
    result_description: Optional[str] = None
    result_image: Optional[str] = None

    rating: Optional[int] = None
    rating_comment: Optional[str] = None

    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    rated_at: Optional[datetime] = None


class OrderStatusUpdate(BaseModel):
    """更新工单状态"""
    status: Literal["处理中", "已结案", "已驳回"]
    result_description: Optional[str] = Field(None, max_length=500)
    result_image: Optional[str] = None
    handler_name: Optional[str] = None


class OrderRating(BaseModel):
    """工单评价"""
    rating: int = Field(ge=1, le=5, description="1-5星")
    comment: Optional[str] = Field(None, max_length=200)


class OrderReportResponse(BaseModel):
    """上报成功响应"""
    order_no: str
    order_id: int
    problem_type: str
    department: Optional[str]
    urgency: str
    points_gained: int
    current_points: int
