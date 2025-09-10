from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


class BaseAppException(Exception):
    """应用基础异常类"""

    def __init__(self, message: str = "Internal Server Error",
                 code: int = HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationException(BaseAppException):
    """数据验证异常"""

    def __init__(self, message: str = "Validation Error", code: int = 400):
        super().__init__(message, code)


class BusinessException(BaseAppException):
    """业务逻辑异常"""

    def __init__(self, message: str = "Business Logic Error", code: int = 400):
        super().__init__(message, code)


class ResourceNotFoundException(BaseAppException):
    """资源未找到异常"""

    def __init__(self, message: str = "Resource Not Found", code: int = 404):
        super().__init__(message, code)


class AuthenticationException(BaseAppException):
    """认证异常"""

    def __init__(self, message: str = "Authentication Failed", code: int = 401):
        super().__init__(message, code)


class AuthorizationException(BaseAppException):
    """授权异常"""

    def __init__(self, message: str = "Authorization Failed", code: int = 403):
        super().__init__(message, code)


class DatabaseException(BaseAppException):
    """数据库操作异常"""

    def __init__(self, message: str = "Database Error", code: int = 500):
        super().__init__(message, code)


class CacheException(BaseAppException):
    """缓存操作异常"""

    def __init__(self, message: str = "Cache Error", code: int = 500):
        super().__init__(message, code)


class ExternalServiceException(BaseAppException):
    """外部服务异常"""

    def __init__(self, message: str = "External Service Error", code: int = 502):
        super().__init__(message, code)
