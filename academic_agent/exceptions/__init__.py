"""
学术Agent异常模块

提供统一的异常处理体系，包括API异常和数据处理异常
"""

from academic_agent.exceptions.base_error import AcademicAgentError
from academic_agent.exceptions.api_error import (
    APIError,
    APIRequestError,
    RateLimitExceededError,
    AuthenticationError,
    APINotAvailableError
)
from academic_agent.exceptions.data_error import (
    DataError,
    PaperNotFoundError,
    AuthorNotFoundError,
    JournalNotFoundError,
    DataValidationError,
    DataConversionError
)

__all__ = [
    # 基础异常
    "AcademicAgentError",
    # API异常
    "APIError",
    "APIRequestError",
    "RateLimitExceededError",
    "AuthenticationError",
    "APINotAvailableError",
    # 数据异常
    "DataError",
    "PaperNotFoundError",
    "AuthorNotFoundError",
    "JournalNotFoundError",
    "DataValidationError",
    "DataConversionError"
]
