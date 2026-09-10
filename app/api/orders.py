"""
工单 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models import Order, User, Admin
from app.schemas.common import success
from app.schemas.order import OrderStatusUpdate, OrderRating, OrderDetail
from app.services.order_service import OrderService

router = APIRouter()


@router.post("/report", summary="市民上报问题（核心接口）")
async def report(
    location: str = Form(...),
    longitude: Optional[str] = Form(None),
    latitude: Optional[str] = Form(None),
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    上传图片/语音/视频/文字到 AI 接口识别，自动生成工单
    需要登录（Header 中携带 Authorization: Bearer <token>）
    """
    order, current_points = OrderService.create_order(
        db=db,
        user=current_user,
        location=location,
        longitude=longitude,
        latitude=latitude,
        image=image,
        audio=audio,
        video=video,
        text=text,
    )

    return success(data={
        "order_no": order.order_no,
        "order_id": order.id,
        "problem_type": order.problem_type,
        "department": order.department.name if order.department else None,
        "urgency": order.urgency,
        "points_gained": 5,
        "current_points": current_points,
    }, message="上报成功")


@router.get("/", summary="工单列表（管理员）")
def list_orders(
    status: Optional[str] = Query(None, description="工单状态"),
    urgency: Optional[str] = Query(None, description="紧急程度"),
    department_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Order).filter(Order.is_deleted == False)

    # 部门管理员只看自己部门的
    if admin.role == "部门管理员" and admin.department_id:
        query = query.filter(Order.department_id == admin.department_id)

    if status:
        query = query.filter(Order.status == status)
    if urgency:
        query = query.filter(Order.urgency == urgency)
    if department_id:
        query = query.filter(Order.department_id == department_id)
    if keyword:
        query = query.filter(or_(
            Order.order_no.contains(keyword),
            Order.problem_type.contains(keyword),
            Order.location.contains(keyword),
            Order.description.contains(keyword),
        ))

    total = query.count()
    orders = query.order_by(Order.created_at.desc())\
                  .offset((page - 1) * page_size).limit(page_size).all()

    return success(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "user_name": o.user.name if o.user else None,
                "problem_type": o.problem_type,
                "department_name": o.department.name if o.department else None,
                "location": o.location,
                "urgency": o.urgency,
                "status": o.status,
                "rating": o.rating,
                "created_at": o.created_at,
            }
            for o in orders
        ]
    })


@router.get("/my", summary="我的上报记录（市民）")
def my_orders(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Order).filter(Order.user_id == current_user.id, Order.is_deleted == False)
    if status:
        query = query.filter(Order.status == status)

    total = query.count()
    orders = query.order_by(Order.created_at.desc())\
                  .offset((page - 1) * page_size).limit(page_size).all()

    return success(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "problem_type": o.problem_type,
                "department_name": o.department.name if o.department else None,
                "location": o.location,
                "urgency": o.urgency,
                "status": o.status,
                "rating": o.rating,
                "created_at": o.created_at,
            }
            for o in orders
        ]
    })


@router.get("/{order_id}", summary="工单详情")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id, Order.is_deleted == False).first()
    if not order:
        raise NotFoundException("工单不存在")

    return success(data={
        "id": order.id,
        "order_no": order.order_no,
        "user_id": order.user_id,
        "user_name": order.user.name if order.user else None,
        "department_id": order.department_id,
        "department_name": order.department.name if order.department else None,
        "problem_type": order.problem_type,
        "multi_department": order.multi_department,
        "confidence": order.confidence,
        "description": order.description,
        "audio_description": order.audio_description,
        "source": order.source,
        "image_path": order.image_path,
        "audio_path": order.audio_path,
        "video_path": order.video_path,
        "location": order.location,
        "longitude": order.longitude,
        "latitude": order.latitude,
        "urgency": order.urgency,
        "status": order.status,
        "handler_name": order.handler_name,
        "result_description": order.result_description,
        "result_image": order.result_image,
        "rating": order.rating,
        "rating_comment": order.rating_comment,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "closed_at": order.closed_at,
        "rated_at": order.rated_at,
    })


@router.put("/{order_id}/status", summary="部门更新工单状态（管理员）")
def update_status(
    order_id: int,
    data: OrderStatusUpdate,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id, Order.is_deleted == False).first()
    if not order:
        raise NotFoundException("工单不存在")

    # 部门管理员只能处理自己部门的工单
    if admin.role == "部门管理员":
        if not admin.department_id or order.department_id != admin.department_id:
            raise ForbiddenException("无权处理此工单")

    handler_name = data.handler_name or admin.real_name or admin.username

    order = OrderService.update_status(
        db=db,
        order_id=order_id,
        status=data.status,
        result_description=data.result_description,
        result_image=data.result_image,
        handler_name=handler_name,
    )
    return success(data={"order_no": order.order_no, "status": order.status}, message="工单状态更新成功")


@router.post("/{order_id}/rate", summary="市民评价工单")
def rate_order(
    order_id: int,
    data: OrderRating,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = OrderService.rate_order(
        db=db,
        order_id=order_id,
        user_id=current_user.id,
        rating=data.rating,
        comment=data.comment,
    )
    return success(data={"order_no": order.order_no, "rating": order.rating}, message="评价成功")
