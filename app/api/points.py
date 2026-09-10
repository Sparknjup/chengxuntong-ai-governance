"""
积分 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, PointsRecord
from app.schemas.common import success

router = APIRouter()


@router.get("/ranking", summary="积分排行榜")
def ranking(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    users = db.query(User)\
        .filter(User.is_deleted == False, User.status == "正常")\
        .order_by(User.points.desc())\
        .limit(limit).all()

    return success(data=[
        {
            "rank": i + 1,
            "user_id": u.id,
            "name": u.name,
            "points": u.points,
            "level": u.level,
        }
        for i, u in enumerate(users)
    ])


@router.get("/my", summary="我的积分明细")
def my_points(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(PointsRecord).filter(PointsRecord.user_id == current_user.id)
    total = query.count()
    records = query.order_by(PointsRecord.created_at.desc())\
                   .offset((page - 1) * page_size).limit(page_size).all()

    return success(data={
        "total_points": current_user.points,
        "level": current_user.level,
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id,
                "points": r.points,
                "points_after": r.points_after,
                "reason": r.reason,
                "order_id": r.order_id,
                "created_at": r.created_at,
            }
            for r in records
        ]
    })
