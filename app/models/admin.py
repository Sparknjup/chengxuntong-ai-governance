"""
管理员模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Admin(Base):
    """系统管理员"""
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password = Column(String(200), nullable=False, comment="密码（bcrypt）")
    real_name = Column(String(50), nullable=True, comment="真实姓名")
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)

    role = Column(String(20), default="部门管理员", nullable=False,
                  comment="超级管理员/部门管理员/指挥中心")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String(50), nullable=True)

    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    department = relationship("Department", back_populates="admins")
