"""HTTP请求工具"""
import time
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """失败重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"请求失败 (尝试 {attempt+1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))
                    else:
                        raise
            return None
        return wrapper
    return decorator


def safe_request(url: str, method: str = "GET", **kwargs) -> Optional[Any]:
    """安全的HTTP请求"""
    try:
        import requests
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    except Exception as e:
        logger.error(f"请求失败: {e}")
        return None


def build_url(base_url: str, endpoint: str, params: Dict[str, Any] = None) -> str:
    """构建URL"""
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    if params:
        query = '&'.join(f"{k}={v}" for k, v in params.items() if v is not None)
        if query:
            url = f"{url}?{query}"
    return url


def parse_response(response: Any) -> Dict[str, Any]:
    """解析响应"""
    if response is None:
        return {}
    try:
        return response.json()
    except Exception:
        return {"text": response.text}


def safe_json_loads(text: str) -> Dict[str, Any]:
    """安全JSON加载"""
    import json
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def add_auth_header(headers: Dict[str, str], api_key: str, auth_type: str = "bearer") -> Dict[str, str]:
    """添加认证头"""
    if auth_type == "bearer":
        headers["Authorization"] = f"Bearer {api_key}"
    elif auth_type == "apikey":
        headers["X-API-Key"] = api_key
    return headers


def get_retry_after(response: Any, default: int = 60) -> int:
    """获取重试时间"""
    try:
        return int(response.headers.get("Retry-After", default))
    except (ValueError, AttributeError):
        return default
