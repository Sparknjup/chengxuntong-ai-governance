"""
文件处理工具
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings
from app.core.exceptions import ValidationException


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_AUDIO_TYPES = {"audio/wav", "audio/mpeg", "audio/mp3", "audio/x-wav", "audio/wave"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/avi", "video/quicktime"}


def ensure_upload_dir(subdir: str = "") -> Path:
    """确保上传目录存在"""
    path = Path(settings.UPLOAD_DIR) / subdir
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_upload_file(file: UploadFile, subdir: str = "") -> str:
    """
    保存上传文件，返回相对路径
    文件名：年月日_uuid.原扩展名
    """
    # 大小检查
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > settings.MAX_UPLOAD_SIZE:
        raise ValidationException(f"文件大小超过限制 {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB")

    # 生成唯一文件名
    ext = Path(file.filename).suffix
    new_name = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:12]}{ext}"

    save_dir = ensure_upload_dir(subdir)
    save_path = save_dir / new_name

    with open(save_path, "wb") as f:
        f.write(file.file.read())
    file.file.seek(0)

    return str(save_path)


def validate_image(file: UploadFile):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValidationException(f"图片仅支持 jpg/png/webp 格式")


def validate_audio(file: UploadFile):
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise ValidationException(f"语音仅支持 wav/mp3 格式")


def validate_video(file: UploadFile):
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise ValidationException(f"视频仅支持 mp4/avi/mov 格式")
