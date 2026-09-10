"""
积分记录模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PointsRecord(Base):
    """积分变动记录"""
    __tablename__ = "points_records"
    __table_args__ = (
        Index("idx_points_user", "user_id"),
        Index("idx_points_created", "created_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    points = Column(Integer, nullable=False, comment="积分变动（正加负减）")
    points_after = Column(Integer, nullable=False, comment="变动后总积分")
    reason = Column(String(100), nullable=False, comment="变动原因")
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, comment="关联工单")
    created_at = Column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", back_populates="points_records")
    order = relationship("Order", back_populates="points_records")
