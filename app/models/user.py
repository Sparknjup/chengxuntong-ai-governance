"""
用户模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """市民用户表"""
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_users_phone", "phone"),
        Index("idx_users_status", "status"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    name = Column(String(50), nullable=False, comment="姓名")
    phone = Column(String(20), unique=True, nullable=False, comment="手机号")
    password = Column(String(200), nullable=False, comment="密码（bcrypt加密）")
    id_card = Column(String(20), nullable=True, comment="身份证号")
    avatar = Column(String(200), nullable=True, comment="头像URL")

    points = Column(Integer, default=0, nullable=False, comment="总积分")
    level = Column(String(20), default="文明参与者", nullable=False, comment="文明等级")

    status = Column(String(10), default="正常", nullable=False, comment="状态：正常/冻结")
    is_deleted = Column(Boolean, default=False, nullable=False, comment="软删除标记")

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # 关系
    orders = relationship("Order", back_populates="user")
    points_records = relationship("PointsRecord", back_populates="user")
