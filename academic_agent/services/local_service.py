"""本地服务模块 - 封装为核心Python包"""
import logging
from typing import Optional, Dict, Any, List
from academic_agent.adapters import get_adapter_class
from academic_agent.qa import (
    BasicQueryModule,
    StatisticalAnalysisModule,
    RelationAnalysisModule,
    DeepResearchModule,
    CustomOutputModule
)
from academic_agent.models import Paper, Author, Journal
from academic_agent.processors import DataCleaner, DataCache, DataConverter
from academic_agent.config import load_config

logger = logging.getLogger(__name__)


class LocalAcademicService:
    """
    本地学术服务
    
    提供统一的本地调用接口，封装所有问答模块功能
    """
    
    # 支持的适配器名称
    SUPPORTED_ADAPTERS = ["openalex", "scopus", "sciencedirect"]
    
    def __init__(self, adapter_name: str = "openalex", config_path: Optional[str] = None):
        """
        初始化本地服务
        
        Args:
            adapter_name: 适配器名称 (openalex/scopus/sciencedirect)
            config_path: 配置文件路径，默认使用内置配置
        """
        if adapter_name not in self.SUPPORTED_ADAPTERS:
            raise ValueError(f"不支持的适配器: {adapter_name}，支持的适配器: {self.SUPPORTED_ADAPTERS}")
        
        self.adapter_name = adapter_name
        
        # 加载配置
        if config_path:
            self.config = load_config(config_path)
        else:
            self.config = load_config()
        
        # 初始化适配器
        adapter_class = get_adapter_class(adapter_name)
        adapter_config = self.config.get("apis", {}).get(adapter_name, {})
        self.adapter = adapter_class(adapter_config)
        
        # 初始化处理器
        processor_config = self.config.get("processors", {})
        self.cleaner = DataCleaner(processor_config)
        self.cache = DataCache(self.config.get("cache", {}))
        self.converter = DataConverter(processor_config)
        
        # 初始化问答模块
        self.basic_query = BasicQueryModule(self.adapter, processor_config)
        self.statistical_analysis = StatisticalAnalysisModule(self.adapter, processor_config)
        self.relation_analysis = RelationAnalysisModule(self.adapter, processor_config)
        self.deep_research = DeepResearchModule(self.adapter, processor_config)
        self.custom_output = CustomOutputModule(self.adapter, processor_config)
        
        logger.info(f"本地服务初始化完成，使用适配器: {adapter_name}")
    
    # ==================== 基础查询接口 ====================
    
    def get_paper_info(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """
        获取论文详细信息
        
        Args:
            paper_id: 论文ID
            
        Returns:
            论文信息字典
        """
        result = self.basic_query.handle({
            "action": "get_paper",
            "paper_id": paper_id
        })
        return result.get("data") if result.get("code") == 200 else None
    
    def get_author_info(self, author_id: str) -> Optional[Dict[str, Any]]:
        """
        获取作者详细信息
        
        Args:
            author_id: 作者ID
            
        Returns:
            作者信息字典
        """
        result = self.basic_query.handle({
            "action": "get_author",
            "author_id": author_id
        })
        return result.get("data") if result.get("code") == 200 else None
    
    def get_author_papers(self, author_id: str, start_year: Optional[int] = None,
                          end_year: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取作者论文列表
        
        Args:
            author_id: 作者ID
            start_year: 开始年份
            end_year: 结束年份
            limit: 数量限制
            
        Returns:
            论文列表
        """
        result = self.basic_query.handle({
            "action": "get_author_papers",
            "author_id": author_id,
            "start_year": start_year,
            "end_year": end_year,
            "limit": limit
        })
        return result.get("data", []) if result.get("code") == 200 else []
    
    def search_papers(self, keyword: str, start_year: Optional[int] = None,
                      end_year: Optional[int] = None, page: int = 1, 
                      page_size: int = 20) -> Dict[str, Any]:
        """
        搜索论文
        
        Args:
            keyword: 搜索关键词
            start_year: 开始年份
            end_year: 结束年份
            page: 页码
            page_size: 每页数量
            
        Returns:
            搜索结果字典
        """
        result = self.basic_query.handle({
            "action": "search_papers",
            "keyword": keyword,
            "start_year": start_year,
            "end_year": end_year,
            "page": page,
            "page_size": page_size
        })
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    def get_journal_info(self, journal_id: str) -> Optional[Dict[str, Any]]:
        """
        获取期刊信息
        
        Args:
            journal_id: 期刊ID
            
        Returns:
            期刊信息字典
        """
        result = self.basic_query.handle({
            "action": "get_journal",
            "journal_id": journal_id
        })
        return result.get("data") if result.get("code") == 200 else None
    
    # ==================== 统计分析接口 ====================
    
    def get_author_yearly_papers(self, author_id: str, start_year: int, 
                                  end_year: int) -> Dict[str, Any]:
        """
        获取作者年度发文量统计
        
        Args:
            author_id: 作者ID
            start_year: 开始年份
            end_year: 结束年份
            
        Returns:
            年度发文量统计
        """
        result = self.statistical_analysis.handle({
            "action": "author_publication_stats",
            "author_id": author_id,
            "start_year": start_year,
            "end_year": end_year
        })
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    def get_keyword_yearly_stats(self, keyword: str, start_year: Optional[int] = None,
                                  end_year: Optional[int] = None) -> Dict[str, Any]:
        """
        获取关键词年度发表量统计
        
        Args:
            keyword: 关键词
            start_year: 开始年份
            end_year: 结束年份
            
        Returns:
            年度发表量统计
        """
        result = self.statistical_analysis.handle({
            "action": "year_distribution",
            "keyword": keyword,
            "start_year": start_year,
            "end_year": end_year
        })
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    def get_top_cited_papers(self, field: str, top_n: int = 10,
                              start_year: Optional[int] = None,
                              end_year: Optional[int] = None) -> Dict[str, Any]:
        """
        获取领域高被引论文TopN
        
        Args:
            field: 研究领域
            top_n: 数量
            start_year: 开始年份
            end_year: 结束年份
            
        Returns:
            高被引论文列表
        """
        result = self.statistical_analysis.handle({
            "action": "author_citation_stats",
            "field": field,
            "top_n": top_n,
            "start_year": start_year,
            "end_year": end_year
        })
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    # ==================== 关联分析接口 ====================
    
    def get_author_cooperation_network(self, author_id: str, depth: int = 1,
                                        min_cooperations: int = 1) -> Dict[str, Any]:
        """
        获取作者合作网络
        
        Args:
            author_id: 作者ID
            depth: 网络深度 (1=直接合作, 2=间接合作)
            min_cooperations: 最小合作次数
            
        Returns:
            合作网络数据
        """
        result = self.relation_analysis.handle({
            "action": "coauthor_network",
            "author_id": author_id,
            "depth": depth,
            "min_cooperations": min_cooperations
        })
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    def get_keyword_cooccurrence(self, keyword: str, top_n: int = 20,
                                  start_year: Optional[int] = None,
                                  end_year: Optional[int] = None) -> Dict[str, Any]:
        """
        获取关键词共现分析
        
        Args:
            keyword: 关键词
            top_n: 数量
            start_year: 开始年份
            end_year: 结束年份
            
        Returns:
            共现分析结果
        """
        result = self.relation_analysis.handle({
            "type": "keyword_cooccurrence",
            "keyword": keyword,
            "top_n": top_n,
            "start_year": start_year,
            "end_year": end_year
        })
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    def get_citation_relations(self, paper_id: str, depth: int = 1) -> Dict[str, Any]:
        """
        获取论文引证关系
        
        Args:
            paper_id: 论文ID
            depth: 关系深度
            
        Returns:
            引证关系数据
        """
        result = self.relation_analysis.handle({
            "action": "citation_network",
            "paper_id": paper_id,
            "depth": depth
        })
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    def get_institution_cooperation(self, institution: str, 
                                     field: Optional[str] = None,
                                     top_n: int = 10) -> Dict[str, Any]:
        """
        获取机构合作分析
        
        Args:
            institution: 机构名称
            field: 研究领域（可选）
            top_n: 数量
            
        Returns:
            机构合作数据
        """
        result = self.relation_analysis.handle({
            "type": "institution_cooperation",
            "institution": institution,
            "field": field,
            "top_n": top_n
        })
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    # ==================== 深度研究接口 ====================
    
    def get_research_trend(self, field: str, time_window: int = 5) -> Dict[str, Any]:
        """
        获取研究方向前沿趋势
        
        Args:
            field: 研究领域
            time_window: 时间窗口（年）
            
        Returns:
            趋势分析结果
        """
        result = self.deep_research.handle({
            "type": "research_trend",
            "field": field,
            "time_window": time_window
        })
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    def get_research_gaps(self, field: str, sub_field: Optional[str] = None) -> Dict[str, Any]:
        """
        识别研究空白
        
        Args:
            field: 研究领域
            sub_field: 子领域（可选）
            
        Returns:
            研究空白分析
        """
        result = self.deep_research.handle({
            "type": "research_gap",
            "field": field,
            "sub_field": sub_field
        })
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    def get_cross_field_analysis(self, field1: str, field2: str) -> Dict[str, Any]:
        """
        跨领域研究关联挖掘
        
        Args:
            field1: 领域1
            field2: 领域2
            
        Returns:
            跨领域分析结果
        """
        result = self.deep_research.handle({
            "type": "cross_field",
            "field1": field1,
            "field2": field2
        })
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    def get_author_evolution(self, author_id: str, time_window: int = 10) -> Dict[str, Any]:
        """
        获取作者研究方向演变
        
        Args:
            author_id: 作者ID
            time_window: 时间窗口（年）
            
        Returns:
            研究方向演变分析
        """
        result = self.deep_research.handle({
            "type": "author_evolution",
            "author_id": author_id,
            "time_window": time_window
        })
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    # ==================== 定制化输出接口 ====================
    
    def export_data(self, data_type: str, params: Dict[str, Any], 
                    format: str = "json") -> Dict[str, Any]:
        """
        导出数据
        
        Args:
            data_type: 数据类型
            params: 查询参数
            format: 输出格式 (json/csv/excel/jsonl/markdown)
            
        Returns:
            导出结果
        """
        result = self.custom_output.handle({
            "type": "export",
            "data_type": data_type,
            "params": params,
            "format": format
        })
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    def generate_chart_data(self, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """
        生成图表数据
        
        Args:
            analysis_type: 分析类型
            **kwargs: 其他参数
            
        Returns:
            图表数据
        """
        params = {"type": "chart_data", "analysis_type": analysis_type}
        params.update(kwargs)
        result = self.custom_output.handle(params)
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    def generate_network_data(self, network_type: str, **kwargs) -> Dict[str, Any]:
        """
        生成网络数据（用于Gephi等工具）
        
        Args:
            network_type: 网络类型
            **kwargs: 其他参数
            
        Returns:
            网络数据
        """
        params = {"type": "network_data", "network_type": network_type}
        params.update(kwargs)
        result = self.custom_output.handle(params)
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    def batch_export(self, keyword_list: List[str], start_year: Optional[int] = None,
                     end_year: Optional[int] = None, format: str = "jsonl") -> Dict[str, Any]:
        """
        批量导出数据
        
        Args:
            keyword_list: 关键词列表
            start_year: 开始年份
            end_year: 结束年份
            format: 输出格式
            
        Returns:
            批量导出结果
        """
        result = self.custom_output.handle({
            "type": "batch_export",
            "keyword_list": keyword_list,
            "start_year": start_year,
            "end_year": end_year,
            "format": format
        })
        return result.get("data", {}) if result.get("code") == 200 else {}
    
    # ==================== 工具方法 ====================
    
    def switch_adapter(self, adapter_name: str) -> None:
        """
        切换适配器
        
        Args:
            adapter_name: 新适配器名称
        """
        if adapter_name not in self.SUPPORTED_ADAPTERS:
            raise ValueError(f"不支持的适配器: {adapter_name}")
        
        adapter_class = get_adapter_class(adapter_name)
        adapter_config = self.config.get("apis", {}).get(adapter_name, {})
        self.adapter = adapter_class(adapter_config)
        
        # 重新初始化问答模块
        self.basic_query = BasicQueryModule(self.adapter, self.config.get("processors", {}))
        self.statistical_analysis = StatisticalAnalysisModule(self.adapter, self.config.get("processors", {}))
        self.relation_analysis = RelationAnalysisModule(self.adapter, self.config.get("processors", {}))
        self.deep_research = DeepResearchModule(self.adapter, self.config.get("processors", {}))
        self.custom_output = CustomOutputModule(self.adapter, self.config.get("processors", {}))
        
        self.adapter_name = adapter_name
        logger.info(f"已切换到适配器: {adapter_name}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return self.cache.get_stats() if hasattr(self.cache, 'get_stats') else {}
    
    def clear_cache(self) -> bool:
        """清空缓存"""
        return self.cache.clear()
