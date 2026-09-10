"""
统计 API
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models import Admin, Order, User, Department, PointsRecord
from app.schemas.common import success

router = APIRouter()


@router.get("/overview", summary="总览数据")
def overview(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    base_query = db.query(Order).filter(Order.is_deleted == False)
    # 部门管理员只看自己部门
    if admin.role == "部门管理员" and admin.department_id:
        base_query = base_query.filter(Order.department_id == admin.department_id)

    total = base_query.count()
    pending = base_query.filter(Order.status == "待处理").count()
    processing = base_query.filter(Order.status == "处理中").count()
    closed = base_query.filter(Order.status == "已结案").count()
    urgent = base_query.filter(Order.urgency == "紧急").count()

    close_rate = round(closed / total * 100, 1) if total > 0 else 0
    avg_rating = base_query.with_entities(func.avg(Order.rating))\
                            .filter(Order.rating != None).scalar()
    avg_rating = round(float(avg_rating), 2) if avg_rating else 0.0

    total_users = db.query(User).filter(User.is_deleted == False).count()

    return success(data={
        "total_orders": total,
        "pending": pending,
        "processing": processing,
        "closed": closed,
        "urgent": urgent,
        "close_rate": f"{close_rate}%",
        "avg_rating": avg_rating,
        "total_users": total_users,
    })


@router.get("/by-type", summary="按问题类型统计")
def stats_by_type(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    query = db.query(Order.problem_type, func.count(Order.id).label("count"))\
              .filter(Order.is_deleted == False)
    if admin.role == "部门管理员" and admin.department_id:
        query = query.filter(Order.department_id == admin.department_id)
    rows = query.group_by(Order.problem_type).all()
    return success(data=[{"type": t or "未分类", "count": c} for t, c in rows])


@router.get("/by-department", summary="按部门统计（超管）")
def stats_by_dept(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    rows = db.query(Department.name, func.count(Order.id).label("count"))\
        .outerjoin(Order, Order.department_id == Department.id)\
        .filter(Department.is_deleted == False)\
        .group_by(Department.name).all()
    return success(data=[{"department": d, "count": c} for d, c in rows])


@router.get("/trend", summary="近7天工单趋势")
def trend(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    today = datetime.now().date()
    result = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        start = datetime.combine(day, datetime.min.time())
        end = start + timedelta(days=1)

        q = db.query(func.count(Order.id))\
              .filter(Order.is_deleted == False)\
              .filter(Order.created_at >= start, Order.created_at < end)

        if admin.role == "部门管理员" and admin.department_id:
            q = q.filter(Order.department_id == admin.department_id)

        result.append({"date": day.strftime("%Y-%m-%d"), "count": q.scalar() or 0})

    return success(data=result)


@router.get("/level-distribution", summary="市民等级分布")
def level_distribution(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    rows = db.query(User.level, func.count(User.id))\
        .filter(User.is_deleted == False)\
        .group_by(User.level).all()
    return success(data=[{"level": l, "count": c} for l, c in rows])
