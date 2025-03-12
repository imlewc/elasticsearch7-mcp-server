# Elasticsearch 7.x MCP Server

[![smithery badge](https://smithery.ai/badge/@imlewc/elasticsearch7-mcp-server)](https://smithery.ai/server/@imlewc/elasticsearch7-mcp-server)

An MCP server for Elasticsearch 7.x, providing compatibility with Elasticsearch 7.x versions.

<a href="https://glama.ai/mcp/servers/zxwxozvlme">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/zxwxozvlme/badge" alt="Elasticsearch 7.x Server MCP server" />
</a>

## Features

- Provides an MCP protocol interface for interacting with Elasticsearch 7.x
- Supports basic Elasticsearch operations (ping, info, etc.)
- Supports complete search functionality, including aggregation queries, highlighting, sorting, and other advanced features
- Easily access Elasticsearch functionality through any MCP client

## Requirements

- Python 3.10+
- Elasticsearch 7.x (7.17.x recommended)

## Installation

### Installing via Smithery

To install Elasticsearch 7.x MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@imlewc/elasticsearch7-mcp-server):

```bash
npx -y @smithery/cli install @imlewc/elasticsearch7-mcp-server --client claude
```

### Manual Installation
```bash
pip install -e .
```

## Environment Variables

The server requires the following environment variables:

- `ELASTIC_HOST`: Elasticsearch host address (e.g., http://localhost:9200)
- `ELASTIC_USERNAME`: Elasticsearch username
- `ELASTIC_PASSWORD`: Elasticsearch password
- `MCP_PORT`: (Optional) MCP server listening port, default 9999

## Using Docker Compose

1. Create a `.env` file and set `ELASTIC_PASSWORD`:

```
ELASTIC_PASSWORD=your_secure_password
```

2. Start the services:

```bash
docker-compose up -d
```

This will start a three-node Elasticsearch 7.17.10 cluster, Kibana, and the MCP server.

## Using an MCP Client

You can use any MCP client to connect to the MCP server:

```python
from mcp import MCPClient

client = MCPClient("localhost:9999")
response = client.call("es-ping")
print(response)  # {"success": true}
```

## API Documentation

Currently supported MCP methods:

- `es-ping`: Check Elasticsearch connection
- `es-info`: Get Elasticsearch cluster information
- `es-search`: Search documents in Elasticsearch index

### Search API Examples

#### Basic Search
```python
# Basic search
search_response = client.call("es-search", {
    "index": "my_index",
    "query": {
        "match": {
            "title": "search keywords"
        }
    },
    "size": 10,
    "from": 0
})
```

#### Aggregation Query
```python
# Aggregation query
agg_response = client.call("es-search", {
    "index": "my_index",
    "size": 0,  # Only need aggregation results, no documents
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

#### Advanced Search
```python
# Advanced search with highlighting, sorting, and filtering
advanced_response = client.call("es-search", {
    "index": "my_index",
    "query": {
        "bool": {
            "must": [
                {"match": {"content": "search term"}}
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

## Development

1. Clone the repository
2. Install development dependencies
3. Run the server: `elasticsearch7-mcp-server`

## License

[License in LICENSE file]

*[中文文档](README-cn.md)*