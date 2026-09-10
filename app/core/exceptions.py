"""
统一异常处理
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.core.logger import logger


class APIException(Exception):
    """业务异常基类"""
    def __init__(self, message: str, code: int = 400, data: dict = None):
        self.message = message
        self.code = code
        self.data = data


class NotFoundException(APIException):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, code=404)


class UnauthorizedException(APIException):
    def __init__(self, message: str = "未授权访问"):
        super().__init__(message, code=401)


class ForbiddenException(APIException):
    def __init__(self, message: str = "无权限"):
        super().__init__(message, code=403)


class ValidationException(APIException):
    def __init__(self, message: str = "参数错误"):
        super().__init__(message, code=400)


class ConflictException(APIException):
    def __init__(self, message: str = "资源冲突"):
        super().__init__(message, code=409)


def register_exception_handlers(app):
    """注册全局异常处理器"""

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        logger.warning(f"业务异常 [{exc.code}] {exc.message} | path={request.url.path}")
        return JSONResponse(
            status_code=exc.code,
            content={"success": False, "code": exc.code, "message": exc.message, "data": exc.data}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = [{"field": ".".join(str(x) for x in e["loc"]), "msg": e["msg"]} for e in exc.errors()]
        logger.warning(f"参数校验失败 {errors} | path={request.url.path}")
        return JSONResponse(
            status_code=422,
            content={"success": False, "code": 422, "message": "参数校验失败", "data": errors}
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "code": exc.status_code, "message": str(exc.detail), "data": None}
        )

    @app.exception_handler(SQLAlchemyError)
    async def db_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.exception(f"数据库异常 {exc} | path={request.url.path}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "code": 500, "message": "数据库错误", "data": None}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception(f"未捕获异常 {exc} | path={request.url.path}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "code": 500, "message": "服务器内部错误", "data": None}
        )
