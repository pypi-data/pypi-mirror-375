from collections.abc import Awaitable
import inspect
import json
from pathlib import Path
from typing import Any, Callable
from fastmcp import FastMCP
from fastmcp.mcp_config import MCPConfig
from fastmcp.server.server import Transport
from fastmcp.server.proxy import FastMCPProxy
from fastmcp.resources.resource import Resource
from fastmcp.prompts.prompt import Prompt, PromptResult
from fastmcp.tools import Tool
from fastmcp.server.http import StarletteWithLifespan
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp import Client
import yaml

from ...Application.Abstractions.External.base_mcp_service import BaseMCPService
from .Middleware.claim_tool_middleware import ClaimsToolsMiddleware
from ...Infrastructure.MCP.Middleware.logging_middleware import LoggingMiddleware


class MCPService(BaseMCPService):
    def __init__(self, name:str='MCPServer'):
        self.__name:str = name
        self.__mcp:FastMCP = None
        self.__lst_tool:list[Tool] = []
        self.__lst_resource:list[Tool] = []
        self.__lst_prompt:list[Tool] = []
        self.__mcp:FastMCP = None
        self.__mcp_app:StarletteWithLifespan|None = None
        self.__jwt_virifier:dict[str, Any] = {}

    @classmethod
    def from_param(cls, name:str, instructions:str|None=None, jwt_virifier:dict={})->'MCPService':
        new_instance:'MCPService' = cls(name)

        if jwt_virifier:
            new_instance.__jwt_virifier = jwt_virifier
            public_key:str = jwt_virifier.get('public_key', None)
            issuer:str = jwt_virifier.get('issuer', '')
            algorithms:str = jwt_virifier.get('algorithms', 'HS256')
            scopes:list[str] = jwt_virifier.get('scopes', [])
            
            if public_key and algorithms:
                jwt_provider = JWTVerifier(
                                    algorithm=algorithms,
                                    public_key=inspect.cleandoc(public_key),
                                    issuer=issuer, 
                                    audience=new_instance.__name,
                                    required_scopes=scopes
                                )
                new_instance.__mcp = FastMCP(name=name, instructions=instructions, auth=jwt_provider)
                new_instance.__mcp.add_middleware(ClaimsToolsMiddleware(new_instance))
            else:
                new_instance.__mcp = FastMCP(name=name, instructions=instructions)
        else:
            new_instance.__mcp = FastMCP(name=name, instructions=instructions)
        
        new_instance.__mcp.add_middleware(LoggingMiddleware())

        return new_instance
    
    @classmethod
    async def as_proxy(cls, client:Client):
        async with client as connected_client:
            proxy = FastMCP.as_proxy(connected_client)
        
        return proxy

    def create_proxy_from_config(self, 
                                 name:str, 
                                 config_file:str,
                                 path:str='/mcp_proxy')->bool:
        try:
            with open(config_file, "r") as f:
                config_dict = yaml.safe_load(f)
                
            config = MCPConfig.from_dict(config_dict)
            proxy = FastMCP.as_proxy(config, name=name)
            self.__mcp.mount(server=proxy)

            return True
        except Exception as ex:
            print(f"ERROR: {ex}")
            
            return False
    
    def create_proxy_from_client(self, 
                                 name:str, 
                                 config_file:str,
                                 path:str='/mcp_proxy')->bool:
        try:
            BASE_URL:str = f"http://192.168.62.223:6506/mcp"
            #BASE_URL:str = f"http://localhost:6506/mcp"
            api_key:str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJLU1VfTUNQIGNsaWVudCIsImV4cCI6MTc1NzQxOTEyOS44MzgwOTIsInN1YmplY3QiOiJ0ZXN0LWNsaWVudCIsImlzcyI6Imh0dHBzOi8vYWkuMWMta3N1LnJ1IiwiYXVkIjoiTUNQIE9rb2YgREIiLCJzY29wZSI6WyJkYXRhOnJlYWQiLCJ3cml0ZSIsInJlYWRfbGlzdF9wcm9qZWN0Il19.U12P0kjMBxKkWlN_2JWN6dt1YuE4OVFdqDMbhgEllbM"
            #api_key:str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJLU1VfTUNQIGNsaWVudCIsImV4cCI6MTc1NzQzNDczNi40ODI3NjMsInN1YmplY3QiOiJ0ZXN0LWNsaWVudCIsImlzcyI6Imh0dHBzOi8vYWkuMWMta3N1LnJ1IiwiYXVkIjoiTUNQIExMTSBzZXJ2aWNlIiwic2NvcGUiOlsiZGF0YTpyZWFkIiwid3JpdGUiXX0.043T-MHmFNbjq0BeIWt04zX-b9mCZRIA2CLSVV1YOw0"
            client:Client = Client(BASE_URL, auth=api_key)
            proxy = FastMCP.as_proxy(client)
            self.__mcp.mount(server=proxy) #, prefix='llm'

            return True
        except Exception as ex:
            print(f"ERROR: {ex}")
            
            return False
        
    """
    from fastmcp.client.transports import StreamableHttpTransport
    @classmethod
    def from_client(cls, name:str, url:str, path:str='vmks01'):
        from fastmcp import Client
        main_mcp = FastMCP(name=name) /mcp
        client = Client(transport=StreamableHttpTransport(url))
        proxy = FastMCP.as_proxy(client, name=path) /proxy/mcp
        main_mcp.mount(key, proxy)
        http_app = main_mcp.http_app("/mcp")
    
    """
    def get_config_key(self, name_key:str)->Any:
        value = self.__jwt_virifier.get(name_key, None)
        
        return value

    def get_http_app(self, path:str='/mcp')->StarletteWithLifespan:
        if not self.__mcp_app:
            self.__mcp_app = self.__mcp.http_app(path)
        
        return self.__mcp_app
    
    def add_tool(self, fn_tool:Callable[..., Any], description:str, tags:set[str], name:str=str(), title:str=str()):
        try:
            tmp_tool = Tool.from_function(fn=fn_tool, name=name, title=title, description=description, tags=tags)
            self.__lst_tool.append(self.__mcp.add_tool(tool=tmp_tool))
        
        except Exception as ex:
            print(f"ERROR(add_tool):{ex}")

    def add_resource(self, fn_tool:Callable[..., Any], uri:str, description:str, tags:set[str], name:str=str(), title:str=str()):
        try:
            tmp_tool = Resource.from_function(fn=fn_tool, uri=uri, name=name, title=title, description=description, tags=tags)
            self.__lst_resource.append(self.__mcp.add_resource(tool=tmp_tool))
        
        except Exception as ex:
            print(f"ERROR(add_resource):{ex}")

    def add_prompt(self, fn_tool:Callable[..., PromptResult | Awaitable[PromptResult]], description:str, tags:set[str], name:str=str(), title:str=str()):
        try:
            tmp_tool = Prompt.from_function(fn=fn_tool, name=name, title=title, description=description, tags=tags)
            self.__lst_prompt.append(self.__mcp.add_prompt(tool=tmp_tool))
        
        except Exception as ex:
            print(f"ERROR(add_prompt):{ex}")

    def run(self, host:str='0.0.0.0', port:int=8000, transport:Transport='streamable-http'):
        self.__mcp.run(transport=transport, host=host, port=port)