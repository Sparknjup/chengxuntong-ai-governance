"""
数据库初始化脚本
- 自动建表
- 写入种子数据（部门、超级管理员）
运行：python -m app.core.init_db
"""
from app.core.database import engine, SessionLocal, Base
from app.core.security import hash_password
from app.core.logger import logger
from app.models import User, Department, Order, PointsRecord, Admin


# 初始部门
INITIAL_DEPARTMENTS = [
    {"name": "道路局", "code": "ROAD", "description": "负责路面、井盖、道路标线等"},
    {"name": "市政局", "code": "MUNICIPAL", "description": "负责路灯、电线杆、护栏等公共设施"},
    {"name": "环卫局", "code": "SANITATION", "description": "负责垃圾、街道清洁等"},
    {"name": "园林局", "code": "GARDEN", "description": "负责绿化、树木、花坛等"},
    {"name": "公安局", "code": "POLICE", "description": "负责治安、紧急求助"},
    {"name": "卫健委", "code": "HEALTH", "description": "负责急救、医疗"},
]


def init_db():
    """初始化数据库"""
    logger.info("开始初始化数据库...")

    # 1. 建表
    Base.metadata.create_all(bind=engine)
    logger.info("数据表创建完成")

    db = SessionLocal()
    try:
        # 2. 写入部门
        for d in INITIAL_DEPARTMENTS:
            if not db.query(Department).filter(Department.name == d["name"]).first():
                db.add(Department(**d))
        db.commit()
        logger.info(f"部门数据初始化完成，共 {len(INITIAL_DEPARTMENTS)} 个")

        # 3. 创建超级管理员（admin / admin123）
        if not db.query(Admin).filter(Admin.username == "admin").first():
            db.add(Admin(
                username="admin",
                password=hash_password("admin123"),
                real_name="超级管理员",
                role="超级管理员",
            ))
            db.commit()
            logger.info("超级管理员账号创建完成：admin / admin123")
        else:
            logger.info("超级管理员账号已存在")

        logger.info("✅ 数据库初始化成功")

    except Exception as e:
        db.rollback()
        logger.exception(f"初始化失败 {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
