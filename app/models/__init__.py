"""
模型导出 - 方便统一import
"""
from app.models.user import User
from app.models.department import Department
from app.models.order import Order
from app.models.points import PointsRecord
from app.models.admin import Admin

__all__ = ["User", "Department", "Order", "PointsRecord", "Admin"]
