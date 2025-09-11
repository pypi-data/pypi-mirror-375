import traceback
from datetime import datetime
from typing import Union

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from lesscode.core.exceptions import BaseAppException
from lesscode.core.logging import get_logger
from lesscode.core.status_codes import get_business_status
from lesscode.schemas.response import ErrorResponse

logger = get_logger(__name__)


async def base_app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """处理自定义应用异常"""
    logger.error(f"Application exception: {exc.message}", extra={
        "path": request.url.path,
        "method": request.method,
        "exception_type": type(exc).__name__
    })

    business_status = get_business_status(exc.code, "400")

    return JSONResponse(
        status_code=exc.code,
        content=ErrorResponse(
            status=business_status,
            message=exc.message,  # 自定义异常的消息已经是用户友好的
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        ).dict()
    )


async def http_exception_handler(request: Request,
                                 exc: Union[HTTPException, StarletteHTTPException]) -> JSONResponse:
    """处理HTTP异常"""
    logger.warning(f"HTTP exception: {exc.detail}", extra={
        "path": request.url.path,
        "method": request.method,
        "status_code": exc.status_code
    })

    business_status = get_business_status(exc.status_code, "400")

    # 提供用户友好的错误消息
    user_friendly_messages = {
        400: "请求参数有误，请检查后重试",
        401: "未授权访问，请先登录",
        403: "权限不足，无法访问该资源",
        404: "请求的资源不存在",
        422: "数据验证失败，请检查输入内容",
        500: "服务暂时不可用，请稍后重试"
    }

    user_message = user_friendly_messages.get(exc.status_code, "请求处理失败，请稍后重试")

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status=business_status,
            message=user_message,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        ).dict()
    )


async def validation_exception_handler(request: Request,
                                       exc: RequestValidationError) -> JSONResponse:
    """处理请求验证异常"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    error_message = "; ".join(errors)

    logger.warning(f"Validation error: {error_message}", extra={
        "path": request.url.path,
        "method": request.method,
        "errors": exc.errors()
    })

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            status="422",
            message=f"数据验证失败: {error_message}",
            data={"errors": exc.errors()},
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        ).dict()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理其他未捕获的异常"""
    error_id = id(exc)  # 生成错误ID
    error_traceback = traceback.format_exc()

    logger.error(
        f"Unhandled exception (ID: {error_id}): {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
            "error_id": error_id,
            "traceback": error_traceback
        }
    )

    # 对用户只显示友好的错误信息，不暴露技术细节
    user_message = "系统繁忙，请稍后重试"

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            status="500",
            message=user_message,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        ).dict()
    )


def register_exception_handlers(app):
    """注册所有异常处理器"""
    app.add_exception_handler(BaseAppException, base_app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
