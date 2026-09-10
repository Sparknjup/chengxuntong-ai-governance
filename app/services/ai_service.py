"""
AI 服务 - 封装对 AI 识别接口的调用
"""
import requests
from typing import Optional, Dict, Any
from fastapi import UploadFile
from app.core.config import settings
from app.core.logger import logger
from app.core.exceptions import APIException


# 紧急关键词（识别后自动标记为紧急）
URGENCY_KEYWORDS = [
    "火灾", "急救", "车祸", "晕倒", "燃气泄漏",
    "紧急", "求救", "受伤", "中毒", "坍塌"
]


class AIService:
    """AI 识别服务"""

    @staticmethod
    def _fallback_result(
        image: Optional[UploadFile] = None,
        audio: Optional[UploadFile] = None,
        video: Optional[UploadFile] = None,
        text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """开发环境降级分类，保证外部识别服务不可用时仍可联调。"""
        content = (text or "").strip()
        rules = [
            (("火灾", "燃气", "受伤", "晕倒", "急救", "治安"), "应急安全", "公安局"),
            (("垃圾", "保洁", "污水", "异味", "清运"), "环境卫生", "环卫局"),
            (("树木", "绿化", "枝叶", "花坛"), "园林绿化", "园林局"),
            (("路灯", "护栏", "座椅", "市政设施"), "市政设施", "市政局"),
            (("道路", "井盖", "积水", "路面", "标线"), "道路出行", "道路局"),
            (("医院", "医疗", "医保"), "医疗服务", "卫健委"),
        ]
        problem_type, department = "其他问题", "市政局"
        for keywords, matched_type, matched_department in rules:
            if any(keyword in content for keyword in keywords):
                problem_type, department = matched_type, matched_department
                break

        if video:
            source = "video"
        elif audio:
            source = "audio_only"
        elif image:
            source = "image"
        else:
            source = "text"

        logger.warning("外部 AI 服务不可用，已使用开发环境本地分类降级")
        return {
            "problem_type": problem_type,
            "department": department,
            "description": content or "市民提交了现场资料，请人工复核。",
            "audio_description": content or None,
            "multi_department": False,
            "confidence": "low",
            "source": source,
        }

    @staticmethod
    def analyze(
        image: Optional[UploadFile] = None,
        audio: Optional[UploadFile] = None,
        video: Optional[UploadFile] = None,
        text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        调用 AI 接口识别城市问题
        返回标准化的识别结果
        """
        files = {}
        data = {}

        try:
            if image:
                image.file.seek(0)
                files["image"] = (image.filename, image.file.read(), image.content_type)

            if audio:
                audio.file.seek(0)
                files["audio"] = (audio.filename, audio.file.read(), audio.content_type)

            if video:
                video.file.seek(0)
                files["video"] = (video.filename, video.file.read(), video.content_type)

            if text:
                data["text"] = text

            if not files and not data:
                raise APIException("请至少提供图片、语音、视频或文字其中一种")

            logger.info(f"调用 AI 接口 url={settings.AI_API_URL} files={list(files.keys())} text={bool(text)}")

            response = requests.post(
                settings.AI_API_URL,
                files=files,
                data=data,
                timeout=settings.AI_API_TIMEOUT,
            )

            if response.status_code != 200:
                logger.error(f"AI 接口返回错误 status={response.status_code} body={response.text}")
                if settings.AI_FALLBACK_ENABLED:
                    return AIService._fallback_result(image, audio, video, text)
                raise APIException(f"AI 识别服务异常 [{response.status_code}]", code=502)

            result = response.json()
            logger.info(f"AI 识别成功 result={result}")
            return result

        except requests.Timeout:
            logger.exception("AI 接口超时")
            if settings.AI_FALLBACK_ENABLED:
                return AIService._fallback_result(image, audio, video, text)
            raise APIException("AI 识别超时，请重试", code=504)
        except requests.RequestException as e:
            logger.exception(f"AI 接口请求失败 {e}")
            if settings.AI_FALLBACK_ENABLED:
                return AIService._fallback_result(image, audio, video, text)
            raise APIException("AI 服务不可用，请稍后重试", code=503)
        except ValueError:
            logger.exception("AI 接口返回了无效 JSON")
            if settings.AI_FALLBACK_ENABLED:
                return AIService._fallback_result(image, audio, video, text)
            raise APIException("AI 识别结果格式异常", code=502)

    @staticmethod
    def detect_urgency(description: str, problem_type: str = "") -> str:
        """根据描述自动判断紧急程度"""
        text = (description or "") + (problem_type or "")
        if any(kw in text for kw in URGENCY_KEYWORDS):
            return "紧急"
        return "普通"
