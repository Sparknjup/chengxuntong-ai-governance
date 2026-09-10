"""
应用配置 - 从环境变量加载
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 应用配置
    APP_NAME: str = "城讯通后端系统"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # 数据库
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "chengxuntong"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 天

    # AI接口
    AI_API_URL: str = "http://47.99.87.154:8000/analyze"
    AI_API_TIMEOUT: int = 30
    AI_FALLBACK_ENABLED: bool = True

    # 文件上传
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB

    # 日志
    LOG_DIR: str = "logs"
    LOG_LEVEL: str = "INFO"

    # 业务规则
    POINTS_REPORT_VALID: int = 5      # 有效上报积分
    POINTS_ORDER_CLOSED: int = 8      # 工单结案奖励
    POINTS_FIVE_STAR: int = 3         # 五星好评奖励
    POINTS_FALSE_REPORT: int = -10    # 虚假上报扣分


settings = Settings()
