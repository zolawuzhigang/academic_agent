"""HTTP服务模块 - 基于FastAPI的RESTful API"""
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ==================== Pydantic模型定义 ====================

class PaperInfoRequest(BaseModel):
    paper_id: str = Field(..., description="论文ID")


class AuthorInfoRequest(BaseModel):
    author_id: str = Field(..., description="作者ID")


class AuthorPapersRequest(BaseModel):
    author_id: str = Field(..., description="作者ID")
    start_year: Optional[int] = Field(None, description="开始年份")
    end_year: Optional[int] = Field(None, description="结束年份")
    limit: int = Field(100, description="数量限制", ge=1, le=500)


class SearchPapersRequest(BaseModel):
    keyword: str = Field(..., description="搜索关键词")
    start_year: Optional[int] = Field(None, description="开始年份")
    end_year: Optional[int] = Field(None, description="结束年份")
    page: int = Field(1, description="页码", ge=1)
    page_size: int = Field(20, description="每页数量", ge=1, le=100)


class YearlyStatsRequest(BaseModel):
    author_id: Optional[str] = Field(None, description="作者ID")
    keyword: Optional[str] = Field(None, description="关键词")
    start_year: int = Field(..., description="开始年份")
    end_year: int = Field(..., description="结束年份")


class TopCitedRequest(BaseModel):
    field: str = Field(..., description="研究领域")
    top_n: int = Field(10, description="数量", ge=1, le=100)
    start_year: Optional[int] = Field(None, description="开始年份")
    end_year: Optional[int] = Field(None, description="结束年份")


class CooperationNetworkRequest(BaseModel):
    author_id: str = Field(..., description="作者ID")
    depth: int = Field(1, description="网络深度", ge=1, le=2)
    min_cooperations: int = Field(1, description="最小合作次数", ge=1)


class KeywordCooccurrenceRequest(BaseModel):
    keyword: str = Field(..., description="关键词")
    top_n: int = Field(20, description="数量", ge=1, le=50)
    start_year: Optional[int] = Field(None, description="开始年份")
    end_year: Optional[int] = Field(None, description="结束年份")


class CitationRelationRequest(BaseModel):
    paper_id: str = Field(..., description="论文ID")
    depth: int = Field(1, description="关系深度", ge=1, le=2)


class InstitutionCooperationRequest(BaseModel):
    institution: str = Field(..., description="机构名称")
    field: Optional[str] = Field(None, description="研究领域")
    top_n: int = Field(10, description="数量", ge=1, le=50)


class ResearchTrendRequest(BaseModel):
    field: str = Field(..., description="研究领域")
    time_window: int = Field(5, description="时间窗口（年）", ge=1, le=20)


class ResearchGapRequest(BaseModel):
    field: str = Field(..., description="研究领域")
    sub_field: Optional[str] = Field(None, description="子领域")


class CrossFieldRequest(BaseModel):
    field1: str = Field(..., description="领域1")
    field2: str = Field(..., description="领域2")


class AuthorEvolutionRequest(BaseModel):
    author_id: str = Field(..., description="作者ID")
    time_window: int = Field(10, description="时间窗口（年）", ge=1, le=30)


class ExportDataRequest(BaseModel):
    data_type: str = Field(..., description="数据类型")
    params: Dict[str, Any] = Field(..., description="查询参数")
    format: str = Field("json", description="输出格式")


class BatchExportRequest(BaseModel):
    keyword_list: List[str] = Field(..., description="关键词列表")
    start_year: Optional[int] = Field(None, description="开始年份")
    end_year: Optional[int] = Field(None, description="结束年份")
    format: str = Field("jsonl", description="输出格式")


class APIResponse(BaseModel):
    code: int = Field(..., description="状态码")
    data: Optional[Any] = Field(None, description="响应数据")
    msg: str = Field(..., description="消息")


# ==================== FastAPI应用 ====================

def create_app(adapter_name: str = "openalex", config_path: Optional[str] = None):
    """创建FastAPI应用"""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError:
        raise ImportError("请安装fastapi: pip install fastapi")

    from academic_agent.services.local_service import LocalAcademicService
    from academic_agent.config import load_config

    config = load_config(config_path) if config_path else load_config()
    service_config = config.get("service", {}).get("http", {})

    app = FastAPI(
        title="Academic Agent API",
        description="低耦合、可插拔的学术Agent HTTP服务",
        version="1.0.0",
        docs_url=service_config.get("docs_url", "/docs"),
        redoc_url="/redoc"
    )

    # 配置CORS
    if service_config.get("cors_enabled", True):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 初始化服务
    service = LocalAcademicService(adapter_name=adapter_name, config_path=config_path)

    # ==================== 基础查询接口 ====================

    @app.post("/api/paper/info", response_model=APIResponse)
    def get_paper_info(request: PaperInfoRequest):
        """获取论文详细信息"""
        result = service.get_paper_info(request.paper_id)
        if result is None:
            raise HTTPException(status_code=404, detail="论文不存在")
        return APIResponse(code=200, data=result, msg="success")

    @app.post("/api/author/info", response_model=APIResponse)
    def get_author_info(request: AuthorInfoRequest):
        """获取作者详细信息"""
        result = service.get_author_info(request.author_id)
        if result is None:
            raise HTTPException(status_code=404, detail="作者不存在")
        return APIResponse(code=200, data=result, msg="success")

    @app.post("/api/author/papers", response_model=APIResponse)
    def get_author_papers(request: AuthorPapersRequest):
        """获取作者论文列表"""
        result = service.get_author_papers(
            request.author_id,
            start_year=request.start_year,
            end_year=request.end_year,
            limit=request.limit
        )
        return APIResponse(code=200, data=result, msg="success")

    @app.post("/api/papers/search", response_model=APIResponse)
    def search_papers(request: SearchPapersRequest):
        """搜索论文"""
        result = service.search_papers(
            request.keyword,
            start_year=request.start_year,
            end_year=request.end_year,
            page=request.page,
            page_size=request.page_size
        )
        return APIResponse(code=200, data=result, msg="success")

    # ==================== 统计分析接口 ====================

    @app.post("/api/analysis/author-yearly", response_model=APIResponse)
    def get_author_yearly_papers(request: YearlyStatsRequest):
        """作者年度发文量统计"""
        if not request.author_id:
            raise HTTPException(status_code=400, detail="缺少author_id参数")
        result = service.get_author_yearly_papers(
            request.author_id,
            request.start_year,
            request.end_year
        )
        return APIResponse(code=200, data=result, msg="success")

    @app.post("/api/analysis/keyword-yearly", response_model=APIResponse)
    def get_keyword_yearly_stats(request: YearlyStatsRequest):
        """关键词年度发表量统计"""
        if not request.keyword:
            raise HTTPException(status_code=400, detail="缺少keyword参数")
        result = service.get_keyword_yearly_stats(
            request.keyword,
            request.start_year,
            request.end_year
        )
        return APIResponse(code=200, data=result, msg="success")

    @app.post("/api/analysis/top-cited", response_model=APIResponse)
    def get_top_cited_papers(request: TopCitedRequest):
        """高被引论文TopN"""
        result = service.get_top_cited_papers(
            request.field,
            request.top_n,
            request.start_year,
            request.end_year
        )
        return APIResponse(code=200, data=result, msg="success")

    # ==================== 关联分析接口 ====================

    @app.post("/api/relation/author-cooperation", response_model=APIResponse)
    def get_author_cooperation_network(request: CooperationNetworkRequest):
        """作者合作网络分析"""
        result = service.get_author_cooperation_network(
            request.author_id,
            request.depth,
            request.min_cooperations
        )
        return APIResponse(code=200, data=result, msg="success")

    @app.post("/api/relation/keyword-cooccurrence", response_model=APIResponse)
    def get_keyword_cooccurrence(request: KeywordCooccurrenceRequest):
        """关键词共现分析"""
        result = service.get_keyword_cooccurrence(
            request.keyword,
            request.top_n,
            request.start_year,
            request.end_year
        )
        return APIResponse(code=200, data=result, msg="success")

    @app.post("/api/relation/citation", response_model=APIResponse)
    def get_citation_relations(request: CitationRelationRequest):
        """论文引证关系分析"""
        result = service.get_citation_relations(request.paper_id, request.depth)
        return APIResponse(code=200, data=result, msg="success")

    @app.post("/api/relation/institution-cooperation", response_model=APIResponse)
    def get_institution_cooperation(request: InstitutionCooperationRequest):
        """机构合作分析"""
        result = service.get_institution_cooperation(
            request.institution,
            request.field,
            request.top_n
        )
        return APIResponse(code=200, data=result, msg="success")

    # ==================== 深度研究接口 ====================

    @app.post("/api/research/trend", response_model=APIResponse)
    def get_research_trend(request: ResearchTrendRequest):
        """研究方向前沿趋势分析"""
        result = service.get_research_trend(request.field, request.time_window)
        return APIResponse(code=200, data=result, msg="success")

    @app.post("/api/research/gap", response_model=APIResponse)
    def get_research_gaps(request: ResearchGapRequest):
        """研究空白识别"""
        result = service.get_research_gaps(request.field, request.sub_field)
        return APIResponse(code=200, data=result, msg="success")

    @app.post("/api/research/cross-field", response_model=APIResponse)
    def get_cross_field_analysis(request: CrossFieldRequest):
        """跨领域研究关联挖掘"""
        result = service.get_cross_field_analysis(request.field1, request.field2)
        return APIResponse(code=200, data=result, msg="success")

    @app.post("/api/research/author-evolution", response_model=APIResponse)
    def get_author_evolution(request: AuthorEvolutionRequest):
        """作者研究方向演变分析"""
        result = service.get_author_evolution(request.author_id, request.time_window)
        return APIResponse(code=200, data=result, msg="success")

    # ==================== 定制化输出接口 ====================

    @app.post("/api/export/data", response_model=APIResponse)
    def export_data(request: ExportDataRequest):
        """数据导出"""
        result = service.export_data(request.data_type, request.params, request.format)
        return APIResponse(code=200, data=result, msg="success")

    @app.post("/api/export/batch", response_model=APIResponse)
    def batch_export(request: BatchExportRequest):
        """批量数据导出"""
        result = service.batch_export(
            request.keyword_list,
            request.start_year,
            request.end_year,
            request.format
        )
        return APIResponse(code=200, data=result, msg="success")

    # ==================== 系统接口 ====================

    @app.get("/health")
    def health_check():
        """健康检查"""
        return {"status": "healthy", "adapter": service.adapter_name}

    @app.get("/api/system/cache-stats", response_model=APIResponse)
    def get_cache_stats():
        """获取缓存统计"""
        result = service.get_cache_stats()
        return APIResponse(code=200, data=result, msg="success")

    @app.post("/api/system/clear-cache", response_model=APIResponse)
    def clear_cache():
        """清空缓存"""
        success = service.clear_cache()
        return APIResponse(code=200, data={"cleared": success}, msg="success")

    return app


def start_server(adapter_name: str = "openalex",
                 config_path: Optional[str] = None,
                 host: str = "0.0.0.0",
                 port: int = 8000):
    """启动HTTP服务"""
    try:
        import uvicorn
    except ImportError:
        raise ImportError("请安装uvicorn: pip install uvicorn")

    app = create_app(adapter_name, config_path)
    uvicorn.run(app, host=host, port=port)


# 如果是直接运行此文件
if __name__ == "__main__":
    import sys
    adapter = sys.argv[1] if len(sys.argv) > 1 else "openalex"
    start_server(adapter_name=adapter)
