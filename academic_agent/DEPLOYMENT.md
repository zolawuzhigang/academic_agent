# 部署文档

本文档详细介绍了 Academic Agent 的各种部署方式，包括本地部署、Docker部署、生产环境部署以及性能优化建议。

## 目录

- [环境要求](#环境要求)
- [本地部署](#本地部署)
- [Docker部署](#docker部署)
- [生产环境部署](#生产环境部署)
- [性能优化](#性能优化)
- [故障排查](#故障排查)

## 环境要求

### 基础环境

| 组件 | 最低版本 | 推荐版本 |
|------|----------|----------|
| Python | 3.9 | 3.11+ |
| pip | 20.0 | 23.0+ |
| (可选) Redis | 6.0 | 7.0+ |

### 系统资源

| 部署模式 | CPU | 内存 | 存储 |
|----------|-----|------|------|
| 开发环境 | 2核 | 4GB | 10GB |
| 生产环境 | 4核+ | 8GB+ | 50GB+ |

## 本地部署

### 1. 安装依赖

```bash
# 克隆仓库
git clone https://github.com/yourusername/academic-agent.git
cd academic-agent

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `config/config.yaml`：

```yaml
apis:
  # OpenAlex - 免费开放API，无需密钥
  openalex:
    base_url: "https://api.openalex.org"
    rate_limit: 10
    retry_times: 3
    retry_delay: 1
    timeout: 30
  
  # Scopus - 需要API Key
  # 申请地址: https://dev.elsevier.com/
  scopus:
    api_key: "your-scopus-api-key"
    base_url: "https://api.elsevier.com/content"
    rate_limit: 0.8  # 约48次/分钟
    retry_times: 3
    retry_delay: 1
    timeout: 30
  
  # ScienceDirect - 需要API Key
  # 申请地址: https://dev.elsevier.com/
  sciencedirect:
    api_key: "your-sciencedirect-api-key"
    base_url: "https://api.elsevier.com/content"
    rate_limit: 0.5  # 约30次/分钟
    retry_times: 3
    retry_delay: 1
    timeout: 30

# 缓存配置
cache:
  enabled: true
  backend: "memory"  # 可选: memory, redis, disk
  ttl: 3600  # 缓存时间（秒）
  
  # Redis配置（当backend为redis时）
  redis:
    host: "localhost"
    port: 6379
    db: 0
    password: null

# 日志配置
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/academic_agent.log"
```

### 3. 启动HTTP服务

```bash
# 方式1: 直接启动
python -m academic_agent.services.http_service

# 方式2: 使用uvicorn（推荐开发环境）
uvicorn academic_agent.services.http_service:create_app --factory

# 方式3: 指定适配器和端口
uvicorn academic_agent.services.http_service:create_app --factory \
    --host 0.0.0.0 \
    --port 8080 \
    --reload  # 开发模式，自动重载

# 方式4: 指定配置
ADAPTER=openalex uvicorn academic_agent.services.http_service:create_app --factory
```

### 4. 验证服务

```bash
# 健康检查
curl http://localhost:8000/health

# 预期响应
# {"status": "healthy", "adapter": "openalex", "version": "1.0.0"}

# 测试搜索接口
curl -X POST http://localhost:8000/api/papers/search \
    -H "Content-Type: application/json" \
    -d '{"keyword": "machine learning", "page_size": 5}'
```

### 5. 访问API文档

启动服务后，访问以下地址查看交互式API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Docker部署

### 1. 创建Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "academic_agent.services.http_service:create_app", \
     "--factory", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  academic-agent:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    environment:
      - ADAPTER=openalex
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 可选: Redis缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### 3. 构建镜像

```bash
# 构建镜像
docker build -t academic-agent:latest .

# 查看镜像
docker images | grep academic-agent
```

### 4. 运行容器

```bash
# 方式1: 直接运行
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  --name academic-agent \
  academic-agent:latest

# 方式2: 使用docker-compose
docker-compose up -d

# 查看日志
docker logs -f academic-agent

# 停止服务
docker-compose down
```

## 生产环境部署

### 使用Gunicorn + Uvicorn

```bash
# 安装gunicorn
pip install gunicorn

# 启动服务（4个worker）
gunicorn academic_agent.services.http_service:create_app \
    --factory \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info

# 后台运行
nohup gunicorn academic_agent.services.http_service:create_app \
    --factory \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 > logs/server.log 2>&1 &
```

### 使用Systemd服务

创建 `/etc/systemd/system/academic-agent.service`：

```ini
[Unit]
Description=Academic Agent Service
After=network.target

[Service]
Type=simple
User=academic
WorkingDirectory=/opt/academic-agent
Environment="PATH=/opt/academic-agent/venv/bin"
Environment="ADAPTER=openalex"
Environment="LOG_LEVEL=INFO"
ExecStart=/opt/academic-agent/venv/bin/gunicorn academic_agent.services.http_service:create_app \
    --factory \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start academic-agent

# 设置开机自启
sudo systemctl enable academic-agent

# 查看状态
sudo systemctl status academic-agent

# 查看日志
sudo journalctl -u academic-agent -f
```

### 使用Nginx反向代理

创建 `/etc/nginx/sites-available/academic-agent`：

```nginx
upstream academic_agent {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.academic-agent.com;

    # 日志配置
    access_log /var/log/nginx/academic-agent.access.log;
    error_log /var/log/nginx/academic-agent.error.log;

    # 静态文件（如果有）
    location /static {
        alias /opt/academic-agent/static;
        expires 30d;
    }

    # API请求
    location / {
        proxy_pass http://academic_agent;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

启用配置：

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/academic-agent /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载配置
sudo systemctl reload nginx
```

### HTTPS配置（使用Certbot）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d api.academic-agent.com

# 自动续期测试
sudo certbot renew --dry-run
```

## 性能优化

### 1. 启用Redis缓存

```yaml
# config/config.yaml
cache:
  enabled: true
  backend: "redis"
  ttl: 3600
  redis:
    host: "localhost"
    port: 6379
    db: 0
    password: null
```

### 2. 调整API频率限制

根据您的API订阅级别调整rate_limit：

```yaml
apis:
  scopus:
    rate_limit: 2.0  # 标准订阅约120次/分钟
    
  sciencedirect:
    rate_limit: 1.0  # 标准订阅约60次/分钟
```

### 3. 使用连接池

```python
# 在适配器中配置连接池
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()

# 配置连接池
adapter = HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
)

session.mount('https://', adapter)
```

### 4. Gunicorn优化

```bash
# 根据CPU核心数调整worker数量
# worker数量 = 2 * CPU核心数 + 1

# 4核CPU
-w 9

# 8核CPU
-w 17

# 完整配置示例
gunicorn academic_agent.services.http_service:create_app \
    --factory \
    -w 9 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --worker-connections 1000 \
    --max-requests 10000 \
    --max-requests-jitter 1000 \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile -
```

### 5. 异步处理大数据量

对于需要处理大量数据的接口，建议使用异步处理：

```python
# 在HTTP服务中配置
@app.post("/api/export/batch")
async def batch_export(params: BatchExportParams, background_tasks: BackgroundTasks):
    """批量导出数据（异步处理）"""
    task_id = str(uuid.uuid4())
    
    # 后台执行导出任务
    background_tasks.add_task(process_batch_export, task_id, params)
    
    return {"code": 200, "data": {"task_id": task_id}, "msg": "任务已提交"}
```

## 故障排查

### 常见问题

#### 1. 服务无法启动

```bash
# 检查端口占用
lsof -i :8000
netstat -tlnp | grep 8000

# 检查日志
tail -f logs/academic_agent.log
```

#### 2. API请求超时

```bash
# 检查网络连接
curl -v https://api.openalex.org/works/W123456789

# 检查API限制
curl -I https://api.openalex.org/works/W123456789
```

#### 3. 内存不足

```bash
# 查看内存使用
free -h

# 查看进程内存
top -p $(pgrep -f academic_agent)

# 限制内存使用（systemd）
# 在service文件中添加
# MemoryLimit=4G
```

#### 4. 缓存不生效

```bash
# 检查Redis连接
redis-cli ping

# 查看缓存键
redis-cli keys "*"

# 清除缓存
redis-cli flushdb
```

### 日志级别调整

```yaml
# config/config.yaml
logging:
  level: "DEBUG"  # 调试时使用
```

### 性能监控

```bash
# 使用curl测试响应时间
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# curl-format.txt 内容:
# time_namelookup: %{time_namelookup}
# time_connect: %{time_connect}
# time_appconnect: %{time_appconnect}
# time_pretransfer: %{time_pretransfer}
# time_redirect: %{time_redirect}
# time_starttransfer: %{time_starttransfer}
# time_total: %{time_total}
```
