"""
数据传输对象模块

该模块定义了应用程序中使用的数据传输对象（DTO）和响应模型，包括：
- 基础响应模型 (BaseResponse)
- 成功响应模型 (SuccessResponse)
- 错误响应模型 (ErrorResponse)
- 分页信息模型 (PageInfo)
- 分页响应模型 (PagedResponse)
"""

from .response import BaseResponse, SuccessResponse, ErrorResponse, PageInfo, PagedResponse

__all__ = [
    "BaseResponse",
    "SuccessResponse",
    "ErrorResponse",
    "PageInfo",
    "PagedResponse"
]