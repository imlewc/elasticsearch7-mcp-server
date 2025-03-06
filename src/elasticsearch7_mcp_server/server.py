import logging
import os
from typing import Dict, Any
from fastmcp import FastMCP
from elasticsearch import Elasticsearch
from .es_client import ElasticsearchClient

class ElasticsearchMCPServer:
    def __init__(self):
        self.logger = self._setup_logger()
        self.es_client = ElasticsearchClient(self.logger).es_client
        self.server = FastMCP(name="ElasticsearchMCPServer")
        self._setup_handlers()

    def _setup_logger(self) -> logging.Logger:
        """Set up and configure logger."""
        logger = logging.getLogger("elasticsearch7-mcp-server")
        logger.setLevel(logging.INFO)
        
        # Add console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _setup_handlers(self):
        """Set up MCP handlers for ES operations."""
        # Add your Elasticsearch 7.x specific handlers here
        self.server.tool(name="es-ping", description="Ping Elasticsearch server")(self._handle_ping)
        self.server.tool(name="es-info", description="Get Elasticsearch info")(self._handle_info)
        self.server.tool(
            name="es-search", 
            description="Search documents in Elasticsearch index"
        )(self._handle_search)
        
        # Add more handlers as needed for your specific use case
    
    def _handle_ping(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping request to Elasticsearch."""
        try:
            result = self.es_client.ping()
            return {"success": result}
        except Exception as e:
            self.logger.error(f"Error pinging Elasticsearch: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _handle_info(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """Get Elasticsearch cluster info."""
        try:
            info = self.es_client.info()
            return {"success": True, "info": info}
        except Exception as e:
            self.logger.error(f"Error getting Elasticsearch info: {str(e)}")
            return {"success": False, "error": str(e)}
            
    def _handle_search(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """Search documents in Elasticsearch index.
        
        Expected request format:
        {
            "index": "index_name",
            "query": {
                "match": {"field": "value"}
            },
            "size": 10,  # optional
            "from": 0,   # optional
            "aggs": {    # optional
                "my_agg": {
                    "terms": {"field": "category"}
                }
            },
            # 支持所有其他Elasticsearch搜索参数
            "sort": [...],
            "highlight": {...},
            "_source": [...],
            ...
        }
        """
        try:
            # 验证请求参数
            if not req.get("index"):
                return {"success": False, "error": "Missing required parameter: index"}
            
            # 提取索引名称
            index = req["index"]
            
            # 构建搜索参数 - 保留所有可能的Elasticsearch搜索参数
            # 除了"index"之外的所有参数都传递给Elasticsearch
            search_params = {k: v for k, v in req.items() if k != "index"}
            
            # 记录搜索请求
            self.logger.info(f"Searching index '{index}' with params: {search_params}")
            
            # 执行搜索
            results = self.es_client.search(index=index, body=search_params)
            return {"success": True, "results": results}
        except Exception as e:
            self.logger.error(f"Error searching Elasticsearch: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def start(self):
        """Start the MCP server."""
        self.logger.info("Starting Elasticsearch 7.x MCP Server")
        self.server.run() 