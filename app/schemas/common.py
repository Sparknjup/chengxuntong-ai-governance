"""
通用响应模型
"""
from typing import Generic, Optional, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """统一响应格式"""
    success: bool = True
    code: int = 200
    message: str = "操作成功"
    data: Optional[T] = None


class PaginationData(BaseModel, Generic[T]):
    """分页数据"""
    total: int = Field(description="总条数")
    page: int = Field(description="当前页")
    page_size: int = Field(description="每页数量")
    items: List[T] = Field(description="数据列表")


def success(data=None, message: str = "操作成功"):
    """快速构造成功响应"""
    return {"success": True, "code": 200, "message": message, "data": data}
