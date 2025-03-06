import logging
import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch, exceptions
import warnings
import inspect
import json

# 尝试导入依赖的包，如果不可用则设置标志
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    warnings.warn("requests模块不可用，RequestsElasticsearchClient将不可用")

# 尝试导入OpenSearch
try:
    from opensearchpy import OpenSearch
    OPENSEARCH_AVAILABLE = True
except ImportError:
    OPENSEARCH_AVAILABLE = False
    warnings.warn("opensearchpy模块不可用，OpenSearch客户端将不可用")

# Monkey patch Elasticsearch版本检查
def _monkey_patch_elasticsearch():
    """
    修改Elasticsearch客户端内部函数以绕过兼容性检查
    """
    try:
        # 尝试找到并替换_get_meta_version函数
        from elasticsearch.client import _normalize_hosts, _get_path_components
        from elasticsearch.transport import Transport
        
        # 替换内部检查函数
        if hasattr(Transport, '_verify_elasticsearch'):
            original_verify = Transport._verify_elasticsearch
            
            def patched_verify(*args, **kwargs):
                # 直接返回True，绕过所有验证
                return True
                
            Transport._verify_elasticsearch = patched_verify
            return True
    except Exception as e:
        warnings.warn(f"无法修改Elasticsearch客户端兼容性检查: {str(e)}")
        return False

# 应用monkey patch
_monkey_patch_result = _monkey_patch_elasticsearch()

# 自定义基于requests的简单客户端
if REQUESTS_AVAILABLE:
    class RequestsElasticsearchClient:
        """一个简单的基于requests的Elasticsearch客户端，没有兼容性检查"""
        
        def __init__(self, hosts, http_auth=None, request_timeout=30, **kwargs):
            self.hosts = hosts
            self.username = http_auth[0] if http_auth else None
            self.password = http_auth[1] if http_auth else None
            self.timeout = request_timeout
            self.session = requests.Session()
            
            # 设置基本认证
            if self.username and self.password:
                self.session.auth = (self.username, self.password)
                
            # 设置基本头信息
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
            
        def _get_url(self, path=""):
            """构建完整URL"""
            base_url = self.hosts[0] if isinstance(self.hosts, list) else self.hosts
            if not base_url.endswith('/'):
                base_url += '/'
            if path.startswith('/'):
                path = path[1:]
            return f"{base_url}{path}"
            
        def ping(self):
            """检查服务器是否可访问"""
            try:
                response = self.session.get(self._get_url(), timeout=self.timeout)
                return response.status_code < 400
            except:
                return False
                
        def info(self):
            """获取服务器信息"""
            try:
                response = self.session.get(self._get_url(), timeout=self.timeout)
                if response.status_code < 400:
                    return response.json()
                return {"error": f"请求失败，状态码: {response.status_code}"}
            except Exception as e:
                return {"error": str(e)}
        
        def search(self, index, body):
            """执行搜索"""
            try:
                url = self._get_url(f"{index}/_search")
                response = self.session.post(url, json=body, timeout=self.timeout)
                return response.json()
            except Exception as e:
                return {"error": str(e)}

class ElasticsearchClient:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        # 禁用Elasticsearch的API兼容性检查
        os.environ["ELASTIC_CLIENT_APIVERSIONING"] = "false"
        
        if _monkey_patch_result:
            self.logger.info("已应用Elasticsearch兼容性检查补丁")
        else:
            self.logger.warning("无法应用Elasticsearch兼容性检查补丁")
        
        # 客户端类型
        self.client_type = os.getenv("ES_CLIENT_TYPE", "elasticsearch").lower()
        if self.client_type == "requests" and not REQUESTS_AVAILABLE:
            self.logger.warning("requests模块不可用，回退到使用elasticsearch客户端")
            self.client_type = "elasticsearch"
        if self.client_type == "opensearch" and not OPENSEARCH_AVAILABLE:
            self.logger.warning("opensearchpy模块不可用，回退到使用elasticsearch客户端")
            self.client_type = "elasticsearch"
            
        self.logger.info(f"使用客户端类型: {self.client_type}")
        
        try:
            self.es_client = self._create_elasticsearch_client()
            # 验证连接
            if self.es_client.ping():
                self.logger.info("成功连接到搜索服务器")
                info = self.es_client.info()
                self.logger.info(f"服务器版本: {info.get('version', {}).get('number', 'unknown')}")
            else:
                self.logger.warning("无法ping通搜索服务器，但连接已建立")
        except exceptions.ConnectionError as e:
            self.logger.error(f"无法连接到搜索服务器: {str(e)}")
            raise
        except exceptions.AuthenticationException as e:
            self.logger.error(f"搜索服务器认证失败: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"连接搜索服务器时发生未知错误: {str(e)}")
            raise

    def _get_es_config(self):
        """Get Elasticsearch configuration from environment variables."""
        # Load environment variables from .env file
        load_dotenv()
        config = {
            "host": os.getenv("ELASTIC_HOST", "http://localhost:9200"),
            "username": os.getenv("ELASTIC_USERNAME"),
            "password": os.getenv("ELASTIC_PASSWORD"),
            "timeout": int(os.getenv("ELASTIC_TIMEOUT", "30"))
        }
        
        if not all([config["username"], config["password"]]):
            self.logger.warning("Missing Elasticsearch credentials. Attempting to connect without authentication.")
            config["username"] = None
            config["password"] = None
        
        return config

    def _create_elasticsearch_client(self):
        """Create and return an Elasticsearch 7.x client using configuration from environment."""
        config = self._get_es_config()

        # Disable SSL warnings
        warnings.filterwarnings("ignore", message=".*SSL certificate verification is disabled.*",)
        
        # 构建基本参数
        es_params = {
            "hosts": [config["host"]],
            "verify_certs": False,
            "ssl_show_warn": False,
            "request_timeout": config["timeout"]
        }
        
        # 如果有认证信息则添加
        if config["username"] and config["password"]:
            es_params["http_auth"] = (config["username"], config["password"])
        
        # 添加所有可能帮助绕过兼容性检查的参数
        es_params["headers"] = {
            "x-elastic-product": "Elasticsearch",
            "Accept": "application/json"
        }
        
        # 根据设置决定使用哪个客户端
        if self.client_type == "opensearch" and OPENSEARCH_AVAILABLE:
            self.logger.info("使用OpenSearch客户端连接")
            return OpenSearch(**es_params)
        elif self.client_type == "requests" and REQUESTS_AVAILABLE:
            self.logger.info("使用基于Requests的客户端连接")
            return RequestsElasticsearchClient(**es_params)
        else:
            self.logger.info("使用Elasticsearch客户端连接")
            return Elasticsearch(**es_params) 