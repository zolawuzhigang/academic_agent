"""数据缓存模块"""
import os
import json
import hashlib
import logging
import pickle
import time
from typing import Optional, Any, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class DataCache:
    """数据缓存管理器，支持文件缓存和Redis缓存"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化缓存管理器

        Args:
            config: 配置字典
                - enabled: 是否启用缓存
                - backend: 缓存后端 (file/redis)
                - ttl: 缓存过期时间（秒）
                - file_path: 文件缓存路径
                - redis: Redis配置
        """
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.backend = self.config.get("backend", "file")
        self.ttl = self.config.get("ttl", 3600)  # 默认1小时

        self._redis_client = None

        if self.backend == "file":
            self.file_path = Path(self.config.get("file_path", "./cache"))
            self.file_path.mkdir(parents=True, exist_ok=True)
        elif self.backend == "redis":
            self._init_redis()

    def _init_redis(self):
        """初始化Redis连接"""
        try:
            import redis
            redis_config = self.config.get("redis", {})
            self._redis_client = redis.Redis(
                host=redis_config.get("host", "localhost"),
                port=redis_config.get("port", 6379),
                db=redis_config.get("db", 0),
                password=redis_config.get("password") or None,
                decode_responses=True
            )
            self._redis_client.ping()
            logger.info("Redis缓存连接成功")
        except ImportError:
            logger.warning("redis库未安装，回退到文件缓存")
            self.backend = "file"
            self.file_path = Path("./cache")
            self.file_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Redis连接失败: {e}，回退到文件缓存")
            self.backend = "file"
            self.file_path = Path("./cache")
            self.file_path.mkdir(parents=True, exist_ok=True)

    def _generate_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """生成缓存键"""
        key_str = json.dumps(params, sort_keys=True, default=str)
        hash_key = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{hash_key}"

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存数据

        Args:
            key: 缓存键

        Returns:
            缓存数据，不存在或过期则返回None
        """
        if not self.enabled:
            return None

        try:
            if self.backend == "file":
                return self._get_file(key)
            elif self.backend == "redis":
                return self._get_redis(key)
        except Exception as e:
            logger.error(f"缓存获取失败: {e}")
            return None

    def _get_file(self, key: str) -> Optional[Any]:
        """从文件获取缓存"""
        cache_file = self.file_path / f"{key}.pkl"

        if not cache_file.exists():
            return None

        # 检查过期时间
        stat = cache_file.stat()
        if time.time() - stat.st_mtime > self.ttl:
            cache_file.unlink()
            return None

        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    def _get_redis(self, key: str) -> Optional[Any]:
        """从Redis获取缓存"""
        if not self._redis_client:
            return None

        data = self._redis_client.get(key)
        if data:
            return pickle.loads(data.encode())
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存数据

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），默认使用配置值

        Returns:
            是否设置成功
        """
        if not self.enabled:
            return False

        ttl = ttl or self.ttl

        try:
            if self.backend == "file":
                return self._set_file(key, value, ttl)
            elif self.backend == "redis":
                return self._set_redis(key, value, ttl)
        except Exception as e:
            logger.error(f"缓存设置失败: {e}")
            return False

    def _set_file(self, key: str, value: Any, ttl: int) -> bool:
        """设置文件缓存"""
        cache_file = self.file_path / f"{key}.pkl"

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
            return True
        except Exception as e:
            logger.error(f"文件缓存设置失败: {e}")
            return False

    def _set_redis(self, key: str, value: Any, ttl: int) -> bool:
        """设置Redis缓存"""
        if not self._redis_client:
            return False

        try:
            data = pickle.dumps(value)
            self._redis_client.setex(key, ttl, data)
            return True
        except Exception as e:
            logger.error(f"Redis缓存设置失败: {e}")
            return False

    def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.enabled:
            return False

        try:
            if self.backend == "file":
                cache_file = self.file_path / f"{key}.pkl"
                if cache_file.exists():
                    cache_file.unlink()
                return True
            elif self.backend == "redis" and self._redis_client:
                self._redis_client.delete(key)
                return True
        except Exception as e:
            logger.error(f"缓存删除失败: {e}")
            return False

    def clear(self) -> bool:
        """清空所有缓存"""
        if not self.enabled:
            return False

        try:
            if self.backend == "file":
                for f in self.file_path.glob("*.pkl"):
                    f.unlink()
                return True
            elif self.backend == "redis" and self._redis_client:
                self._redis_client.flushdb()
                return True
        except Exception as e:
            logger.error(f"缓存清空失败: {e}")
            return False

    def cached(self, prefix: str, ttl: Optional[int] = None):
        """
        缓存装饰器

        Args:
            prefix: 缓存键前缀
            ttl: 过期时间

        Returns:
            装饰器函数
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = self._generate_key(prefix, {
                    "args": args,
                    "kwargs": kwargs
                })

                # 尝试获取缓存
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"缓存命中: {cache_key}")
                    return cached_value

                # 执行函数
                result = func(*args, **kwargs)

                # 设置缓存
                self.set(cache_key, result, ttl)

                return result

            return wrapper
        return decorator
