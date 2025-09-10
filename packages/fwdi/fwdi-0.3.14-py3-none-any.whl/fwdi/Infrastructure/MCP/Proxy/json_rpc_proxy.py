from ..mcp_client import MCPClient


class JsonRpcProxy():
    def __init__(self):
        self.__client:MCPClient|None = None
    

    def __init_service(self):
        ...