from datetime import datetime
from math import ceil
from typing import Any, Optional, List, TypeVar

from fastapi.responses import JSONResponse

from lesscode.schemas.response import SuccessResponse, ErrorResponse, PagedResponse, PageInfo

T = TypeVar('T')


class ResponseUtil:
    """响应工具类"""

    @staticmethod
    def success(
            data: Any = None,
            message: str = "请求成功",
            status: str = "00000"
    ) -> dict:
        """生成成功响应"""
        response = SuccessResponse[Any](
            status=status,
            message=message,
            data=data,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        )
        return response.dict(exclude_none=False)

    @staticmethod
    def error(
            message: str = "请求失败",
            status: str = "99999",
            data: Optional[dict] = None
    ) -> dict:
        """生成错误响应"""
        response = ErrorResponse(
            status=status,
            message=message,
            data=data,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        )
        return response.dict(exclude_none=False)

    @staticmethod
    def paged(
            data: List[Any],
            page: int,
            page_size: int,
            total: int,
            message: str = "请求成功",
            status: str = "00000"
    ) -> dict:
        """生成分页响应"""
        total_pages = ceil(total / page_size) if page_size > 0 else 0

        page_info = PageInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )

        response = PagedResponse[Any](
            status=status,
            message=message,
            data=data,
            page_info=page_info,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        )
        return response.dict(exclude_none=False)


# 便捷函数
def success_response(
        data: Any = None,
        message: str = "请求成功",
        status: str = "00000"
) -> dict:
    """成功响应快捷函数"""
    return ResponseUtil.success(data=data, message=message, status=status)


def error_response(
        message: str = "请求失败",
        status: str = "99999",
        data: Optional[dict] = None
) -> dict:
    """错误响应快捷函数"""
    return ResponseUtil.error(message=message, status=status, data=data)


def paged_response(
        data: List[Any],
        page: int,
        page_size: int,
        total: int,
        message: str = "请求成功"
) -> dict:
    """分页响应快捷函数"""
    return ResponseUtil.paged(
        data=data,
        page=page,
        page_size=page_size,
        total=total,
        message=message
    )


def json_response(
        data: Any = None,
        message: str = "请求成功",
        status: str = "00000",
        status_code: int = 200
) -> JSONResponse:
    """返回JSON响应"""
    content = success_response(data=data, message=message, status=status)
    return JSONResponse(content=content, status_code=status_code)
