# Elasticsearch 7.x MCP Server

一个用于 Elasticsearch 7.x 的 MCP 服务器，提供与 Elasticsearch 7.x 版本的兼容性。

## 功能

- 提供 MCP 协议接口与 Elasticsearch 7.x 交互
- 支持基本的 Elasticsearch 操作（ping、info 等）
- 支持完整的搜索功能，包括聚合查询、高亮显示、排序等高级特性
- 可以方便地通过 MCP 客户端访问 Elasticsearch 功能

## 要求

- Python 3.10+
- Elasticsearch 7.x (推荐 7.17.x)

## 安装

```bash
pip install -e .
```

## 环境变量

服务器需要以下环境变量：

- `ELASTIC_HOST`：Elasticsearch 主机地址（如 http://localhost:9200）
- `ELASTIC_USERNAME`：Elasticsearch 用户名
- `ELASTIC_PASSWORD`：Elasticsearch 密码
- `MCP_PORT`：（可选）MCP 服务器监听端口，默认 9999

## 使用 Docker Compose

1. 创建 `.env` 文件并设置 `ELASTIC_PASSWORD`：

```
ELASTIC_PASSWORD=your_secure_password
```

2. 启动服务：

```bash
docker-compose up -d
```

这将启动一个三节点的 Elasticsearch 7.17.10 集群，Kibana 和 MCP 服务器。

## 使用 MCP 客户端

可以使用任何 MCP 客户端连接到 MCP 服务器：

```python
from mcp import MCPClient

client = MCPClient("localhost:9999")
response = client.call("es-ping")
print(response)  # {"success": true}
```

## API 说明

目前支持的 MCP 方法：

- `es-ping`：检查 Elasticsearch 连接
- `es-info`：获取 Elasticsearch 集群信息
- `es-search`：在 Elasticsearch 中搜索文档

### 搜索 API 示例

#### 基本搜索
```python
# 基本搜索
search_response = client.call("es-search", {
    "index": "my_index",
    "query": {
        "match": {
            "title": "搜索关键词"
        }
    },
    "size": 10,
    "from": 0
})
```

#### 聚合查询
```python
# 聚合查询
agg_response = client.call("es-search", {
    "index": "my_index",
    "size": 0,  # 只需要聚合结果，不需要文档
    "aggs": {
        "categories": {
            "terms": {
                "field": "category.keyword",
                "size": 10
            }
        },
        "avg_price": {
            "avg": {
                "field": "price"
            }
        }
    }
})
```

#### 高级搜索
```python
# 带有高亮、排序和过滤的高级搜索
advanced_response = client.call("es-search", {
    "index": "my_index",
    "query": {
        "bool": {
            "must": [
                {"match": {"content": "搜索词"}}
            ],
            "filter": [
                {"range": {"price": {"gte": 100, "lte": 200}}}
            ]
        }
    },
    "sort": [
        {"date": {"order": "desc"}},
        "_score"
    ],
    "highlight": {
        "fields": {
            "content": {}
        }
    },
    "_source": ["title", "date", "price"]
})
```

## 开发

1. 克隆仓库
2. 安装开发依赖
3. 运行服务器：`elasticsearch7-mcp-server`

## 许可

[LICENSE 文件中的许可证] 