import logging
import sys
from .server import ElasticsearchMCPServer

def main():
    """Entry point for the Elasticsearch 7.x MCP server."""
    try:
        server = ElasticsearchMCPServer()
        server.start()
    except Exception as e:
        logging.error(f"Error starting server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 