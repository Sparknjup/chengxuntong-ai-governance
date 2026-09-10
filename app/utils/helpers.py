"""
辅助工具
"""
from datetime import datetime
import secrets


def generate_order_no() -> str:
    """生成工单号：WD + 时间戳 + 随机4位"""
    return f"WD{datetime.now().strftime('%Y%m%d%H%M%S')}{secrets.randbelow(10000):04d}"
