"""
部门模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Department(Base):
    """职能部门表"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, comment="部门名称")
    code = Column(String(20), unique=True, nullable=True, comment="部门编码")
    contact = Column(String(50), nullable=True, comment="联系人")
    phone = Column(String(20), nullable=True, comment="联系电话")
    description = Column(String(200), nullable=True, comment="部门职责")

    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    orders = relationship("Order", back_populates="department")
    admins = relationship("Admin", back_populates="department")
