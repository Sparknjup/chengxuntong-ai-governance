"""
工单业务逻辑
"""
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.core.config import settings
from app.core.logger import logger
from app.core.exceptions import NotFoundException, ValidationException, ConflictException
from app.models import Order, Department, User
from app.services.ai_service import AIService
from app.services.points_service import PointsService
from app.utils.file import save_upload_file, validate_image, validate_audio, validate_video
from app.utils.helpers import generate_order_no


class OrderService:

    @staticmethod
    def create_order(
        db: Session,
        user: User,
        location: str,
        longitude: Optional[str] = None,
        latitude: Optional[str] = None,
        image: Optional[UploadFile] = None,
        audio: Optional[UploadFile] = None,
        video: Optional[UploadFile] = None,
        text: Optional[str] = None,
    ) -> Tuple[Order, int]:
        """
        创建工单的核心流程：
        1. 校验文件格式
        2. 保存文件到本地
        3. 调用 AI 接口识别
        4. 匹配归属部门
        5. 判断紧急程度
        6. 生成工单
        7. 加积分
        返回 (工单, 当前积分)
        """
        # 1. 文件校验
        if image:
            validate_image(image)
        if audio:
            validate_audio(audio)
        if video:
            validate_video(video)

        # 2. 保存文件
        image_path = save_upload_file(image, "images") if image else None
        audio_path = save_upload_file(audio, "audios") if audio else None
        video_path = save_upload_file(video, "videos") if video else None

        # 3. 调用 AI 识别
        ai_result = AIService.analyze(image=image, audio=audio, video=video, text=text)

        # 4. 匹配部门（取第一个，多部门情况后续可扩展）
        dept_name = (ai_result.get("department") or "").split(",")[0].strip()
        department = db.query(Department).filter(
            Department.name == dept_name,
            Department.is_deleted == False
        ).first()

        # 5. 紧急程度
        urgency = AIService.detect_urgency(
            ai_result.get("description", ""),
            ai_result.get("problem_type", "")
        )

        # 6. 创建工单
        order = Order(
            order_no=generate_order_no(),
            user_id=user.id,
            department_id=department.id if department else None,
            problem_type=ai_result.get("problem_type", "未分类"),
            multi_department=ai_result.get("multi_department", False),
            confidence=ai_result.get("confidence"),
            description=ai_result.get("description", ""),
            audio_description=ai_result.get("audio_description"),
            source=ai_result.get("source", "image"),
            image_path=image_path,
            audio_path=audio_path,
            video_path=video_path,
            location=location,
            longitude=longitude,
            latitude=latitude,
            urgency=urgency,
            status="待处理",
        )
        db.add(order)
        db.flush()  # 拿到 order.id 但不提交

        # 7. 加积分（基础上报积分）
        new_points = PointsService.change_points(
            db, user.id,
            settings.POINTS_REPORT_VALID,
            "有效上报基础积分",
            order_id=order.id,
            commit=False,
        )

        db.commit()
        db.refresh(order)

        logger.info(f"工单创建成功 order_no={order.order_no} dept={dept_name} urgency={urgency}")
        return order, new_points

    @staticmethod
    def update_status(
        db: Session,
        order_id: int,
        status: str,
        result_description: Optional[str] = None,
        result_image: Optional[str] = None,
        handler_name: Optional[str] = None,
    ) -> Order:
        """更新工单状态"""
        order = db.query(Order).filter(Order.id == order_id, Order.is_deleted == False).first()
        if not order:
            raise NotFoundException("工单不存在")

        if order.status == "已结案":
            raise ConflictException("工单已结案，不可修改")

        order.status = status
        if result_description is not None:
            order.result_description = result_description
        if result_image is not None:
            order.result_image = result_image
        if handler_name is not None:
            order.handler_name = handler_name

        # 结案处理
        if status == "已结案":
            order.closed_at = datetime.now()
            PointsService.change_points(
                db, order.user_id,
                settings.POINTS_ORDER_CLOSED,
                f"工单【{order.order_no}】处理完成奖励",
                order_id=order.id,
                commit=False,
            )

        db.commit()
        db.refresh(order)
        logger.info(f"工单状态更新 order_no={order.order_no} status={status}")
        return order

    @staticmethod
    def rate_order(
        db: Session,
        order_id: int,
        user_id: int,
        rating: int,
        comment: Optional[str] = None
    ) -> Order:
        """市民评价工单"""
        order = db.query(Order).filter(Order.id == order_id, Order.is_deleted == False).first()
        if not order:
            raise NotFoundException("工单不存在")
        if order.user_id != user_id:
            raise ValidationException("不能评价他人的工单")
        if order.status != "已结案":
            raise ValidationException("工单未结案，无法评价")
        if order.rating is not None:
            raise ConflictException("已评价，不可重复评价")

        order.rating = rating
        order.rating_comment = comment
        order.rated_at = datetime.now()

        # 五星好评额外加分
        if rating == 5:
            PointsService.change_points(
                db, user_id,
                settings.POINTS_FIVE_STAR,
                f"工单【{order.order_no}】五星好评奖励",
                order_id=order.id,
                commit=False,
            )

        db.commit()
        db.refresh(order)
        logger.info(f"工单评价 order_no={order.order_no} rating={rating}")
        return order
