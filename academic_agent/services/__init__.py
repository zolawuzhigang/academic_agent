"""服务层模块"""

from academic_agent.services.local_service import LocalAcademicService
from academic_agent.services.http_service import create_app, start_server

__all__ = ["LocalAcademicService", "create_app", "start_server"]
