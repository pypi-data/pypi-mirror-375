from typing import Any, overload
from fastmcp import Client
from mcp.types import CallToolResult, GetPromptResult, TextResourceContents, BlobResourceContents
from ...Application.Abstractions.External.base_mcp_client import BaseMCPClient

class MCPClient(BaseMCPClient):
    def __init__(self, api_key:str|None=None, host:str='127.0.0.1', port:int=6504, path:str='mcp'):
        super().__init__()
        self.__base_url:str = f"http://{host}:{port}/{path}"

        if api_key:
            self.__client:Client = Client(self.__base_url, auth=api_key)
        else:
            self.__client:Client = Client(self.__base_url)

    @classmethod
    def create_from_url(cls, url:str, api_key:str|None=None):
        instance = cls()
        instance.__base_url = url
        if api_key:
            instance.__client = Client(url, auth=api_key)
        else:
            instance.__client = Client(url)

    async def connect(self):
        await self.__client.__aenter__()

    async def disconnect(self):
        await self.__client.__aexit__()

    async def check_avaible(self):
        return True if await self.__client.ping() else False
    
    async def load_env(self)->bool:
        try:
            if await self.__client.ping():
                self.tools = await self.__client.list_tools()
                self.prompts = await self.__client.list_prompts()
                self.resources = await self.__client.list_resources()
                
                return True
            
            return False
        except Exception as ex:
            print(f"ERROR:{ex}")
            return False
    
    def is_connected(self)->bool:
        return self.__client.is_connected()

    async def ping(self)->bool:
        return await self.__client.ping()

    async def call_tool(self, name_fn:str, param:dict[str, Any]=None)->CallToolResult:
        if param:
            result = await self.__client.call_tool(name_fn, param)
        else:
            result = await self.__client.call_tool(name_fn)

        return result

    async def read_resource(self, uri:str)->list[TextResourceContents | BlobResourceContents]:
        result = await self.__client.read_resource(uri)

        return result

    async def get_prompt(self, name:str, param:dict[str, Any]=None)->GetPromptResult:
        if param:
            result = await self.__client.get_prompt(name, arguments=param)
        else:
            result = await self.__client.get_prompt(name)

        return result