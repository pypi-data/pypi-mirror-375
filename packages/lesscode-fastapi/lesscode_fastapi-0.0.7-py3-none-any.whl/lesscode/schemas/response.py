from datetime import datetime
from typing import Generic, TypeVar, Optional, Any, Dict, List
from pydantic import BaseModel, Field


T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """统一响应基类"""
    status: str = Field(default="00000", description="响应状态码")
    message: str = Field(default="请求成功", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                           description="时间戳")
    class Config:
        json_schema_extra = {
            "example": {
                "status": "00000",
                "message": "请求成功",
                "data": None,
                "timestamp": "2025-09-09 17:43:23.891644"
            }
        }


class SuccessResponse(BaseResponse[T]):
    """成功响应类"""
    status: str = Field(default="00000")
    message: str = Field(default="请求成功")


class ErrorResponse(BaseResponse[None]):
    """错误响应类"""
    status: str = Field(default="10001")
    message: str = Field(default="请求失败")
    data: Optional[Dict[str, Any]] = Field(default=None, description="错误详情")


class PageInfo(BaseModel):
    """分页信息"""
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    total: int = Field(description="总数量")
    total_pages: int = Field(description="总页数")
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")


class PagedResponse(SuccessResponse[List[T]]):
    """分页响应类"""
    data: Optional[List[T]] = Field(default=None)
    page_info: Optional[PageInfo] = Field(default=None, description="分页信息")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "00000",
                "message": "请求成功",
                "data": [],
                "page_info": {
                    "page": 1,
                    "page_size": 20,
                    "total": 100,
                    "total_pages": 5,
                    "has_next": True,
                    "has_prev": False
                },
                "timestamp": "2025-09-09 17:43:23.891644"
            }
        }
