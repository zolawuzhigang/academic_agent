"""配置模块"""
import os
import yaml
from typing import Dict, Any
from pathlib import Path

# 默认配置
DEFAULT_CONFIG = {
    "apis": {
        "openalex": {
            "base_url": "https://api.openalex.org",
            "rate_limit": 10,
            "retry_times": 3,
            "retry_delay": 1,
            "timeout": 30
        },
        "scopus": {
            "base_url": "https://api.elsevier.com/content",
            "api_key": "",
            "rate_limit": 0.8,
            "retry_times": 3,
            "retry_delay": 2,
            "timeout": 30
        },
        "sciencedirect": {
            "base_url": "https://api.elsevier.com/content",
            "api_key": "",
            "rate_limit": 0.5,
            "retry_times": 3,
            "retry_delay": 2,
            "timeout": 30
        }
    },
    "cache": {
        "enabled": True,
        "backend": "file",
        "ttl": 3600,
        "file_path": "./cache"
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "service": {
        "http": {
            "host": "0.0.0.0",
            "port": 8000,
            "cors_enabled": True,
            "docs_url": "/docs"
        },
        "default_adapter": "openalex"
    }
}

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    加载配置
    
    Args:
        config_path: 配置文件路径，默认查找config.yaml
        
    Returns:
        配置字典
    """
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = yaml.safe_load(f)
            # 合并配置
            config = DEFAULT_CONFIG.copy()
            _deep_update(config, user_config)
            return config
    
    # 查找默认配置文件
    possible_paths = [
        "config.yaml",
        "config/config.yaml",
        "./config/config.yaml",
        "../config/config.yaml",
        Path(__file__).parent / "config.yaml"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
                config = DEFAULT_CONFIG.copy()
                _deep_update(config, user_config)
                return config
    
    # 返回默认配置
    return DEFAULT_CONFIG.copy()

def _deep_update(base: Dict, update: Dict) -> Dict:
    """深度更新字典"""
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_update(base[key], value)
        else:
            base[key] = value
    return base

def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    保存配置到文件
    
    Args:
        config: 配置字典
        config_path: 配置文件路径
    """
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def get_api_config(config: Dict[str, Any], api_name: str) -> Dict[str, Any]:
    """
    获取指定API的配置
    
    Args:
        config: 全局配置字典
        api_name: API名称
        
    Returns:
        API配置字典
    """
    return config.get("apis", {}).get(api_name, {})


def get_cache_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取缓存配置
    
    Args:
        config: 全局配置字典
        
    Returns:
        缓存配置字典
    """
    return config.get("cache", {})


def get_logging_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取日志配置
    
    Args:
        config: 全局配置字典
        
    Returns:
        日志配置字典
    """
    return config.get("logging", {})


def get_service_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取服务配置
    
    Args:
        config: 全局配置字典
        
    Returns:
        服务配置字典
    """
    return config.get("service", {})


__all__ = [
    "load_config",
    "save_config",
    "get_api_config",
    "get_cache_config",
    "get_logging_config",
    "get_service_config",
    "DEFAULT_CONFIG"
]
