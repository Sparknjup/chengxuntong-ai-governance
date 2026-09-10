"""
工单模型 - 核心业务实体
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Order(Base):
    """工单表"""
    __tablename__ = "orders"
    __table_args__ = (
        Index("idx_orders_status", "status"),
        Index("idx_orders_urgency", "urgency"),
        Index("idx_orders_user", "user_id"),
        Index("idx_orders_dept", "department_id"),
        Index("idx_orders_created", "created_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(30), unique=True, nullable=False, comment="工单编号")

    # 关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="上报市民")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, comment="归属部门")

    # AI识别结果
    problem_type = Column(String(50), nullable=False, comment="问题类型")
    multi_department = Column(Boolean, default=False, comment="是否多部门协同")
    confidence = Column(String(10), nullable=True, comment="AI置信度 high/medium/low")
    description = Column(String(200), nullable=False, comment="问题描述")
    audio_description = Column(String(500), nullable=True, comment="语音/文字原文")
    source = Column(String(20), nullable=False, comment="识别来源 image/video/audio_only")

    # 文件
    image_path = Column(String(300), nullable=True, comment="图片路径")
    audio_path = Column(String(300), nullable=True, comment="语音路径")
    video_path = Column(String(300), nullable=True, comment="视频路径")

    # 业务字段
    location = Column(String(100), nullable=False, comment="位置信息")
    longitude = Column(String(20), nullable=True, comment="经度")
    latitude = Column(String(20), nullable=True, comment="纬度")
    urgency = Column(String(10), default="普通", nullable=False, comment="紧急程度 紧急/普通")
    status = Column(String(20), default="待处理", nullable=False, comment="待处理/处理中/已结案/已驳回")

    # 处理结果
    handler_name = Column(String(50), nullable=True, comment="处理人")
    result_description = Column(Text, nullable=True, comment="处理结果")
    result_image = Column(String(300), nullable=True, comment="处理结果图片")

    # 评价
    rating = Column(Integer, nullable=True, comment="市民评分 1-5")
    rating_comment = Column(String(200), nullable=True, comment="评价内容")

    # 软删除
    is_deleted = Column(Boolean, default=False, nullable=False)

    # 时间戳
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    closed_at = Column(DateTime, nullable=True, comment="结案时间")
    rated_at = Column(DateTime, nullable=True, comment="评价时间")

    # 关系
    user = relationship("User", back_populates="orders")
    department = relationship("Department", back_populates="orders")
    points_records = relationship("PointsRecord", back_populates="order")
