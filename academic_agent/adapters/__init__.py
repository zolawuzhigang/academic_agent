"""API适配器模块"""

from academic_agent.adapters.base_adapter import BaseAcademicAdapter


def get_adapter_class(adapter_name: str):
    """
    根据名称获取适配器类

    Args:
        adapter_name: 适配器名称 (openalex, scopus, sciencedirect)

    Returns:
        适配器类
    """
    adapter_map = {
        "openalex": "academic_agent.adapters.openalex_adapter.OpenAlexAdapter",
        "scopus": "academic_agent.adapters.scopus_adapter.ScopusAdapter",
        "sciencedirect": "academic_agent.adapters.sciencedirect_adapter.ScienceDirectAdapter"
    }

    if adapter_name not in adapter_map:
        raise ValueError(f"不支持的适配器: {adapter_name}，支持的适配器: {list(adapter_map.keys())}")

    # 动态导入
    module_path, class_name = adapter_map[adapter_name].rsplit(".", 1)
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)


__all__ = ["BaseAcademicAdapter", "get_adapter_class"]
