"""
积分服务
"""
from sqlalchemy.orm import Session
from app.models import User, PointsRecord
from app.core.logger import logger


def get_level_by_points(points: int) -> str:
    """根据积分计算等级"""
    if points >= 501:
        return "五星文明市民"
    elif points >= 301:
        return "四星文明市民"
    elif points >= 101:
        return "三星文明市民"
    else:
        return "文明参与者"


class PointsService:

    @staticmethod
    def change_points(
        db: Session,
        user_id: int,
        points: int,
        reason: str,
        order_id: int = None,
        commit: bool = True
    ) -> int:
        """
        给用户加减积分（同时记录历史、更新等级）
        返回变动后的总积分
        """
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            logger.warning(f"积分变动失败，用户不存在 user_id={user_id}")
            return 0

        # 累计积分，不允许小于0
        new_points = max(0, user.points + points)
        user.points = new_points
        user.level = get_level_by_points(new_points)

        # 写入历史
        record = PointsRecord(
            user_id=user_id,
            points=points,
            points_after=new_points,
            reason=reason,
            order_id=order_id,
        )
        db.add(record)

        if commit:
            db.commit()

        logger.info(f"积分变动 user_id={user_id} change={points} after={new_points} reason={reason}")
        return new_points
