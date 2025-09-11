import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, AsyncIterator

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel import NotificationOptions
from mcp import types

from fwdi.Infrastructure.MCP.Base.client_json_rpc import ClientJsonRPC
from ....Infrastructure.MCP.Base.config import Config


class CustomMCPServer():
	
	def __init__(self, config: Config):
		self.config:Config = config
		self.json_rpc_client:ClientJsonRPC|None = None
		
		self.server = Server(
			name=config.service_name,
			lifespan=self._lifespan
		)
		
		self.__register_handlers()
	
	@asynccontextmanager
	async def _lifespan(self, server: Server)->AsyncIterator[Dict[str, Any]]:
		CustomMCPServer.__log__(f"Init MCP service '{self.config.service_name}' v{self.config.server_version}", 'debug')
		
		self.json_rpc_client = ClientJsonRPC(
			base_url=self.config.base_url,
			username=self.config.username,
			password=self.config.password,
			service_root=self.config.service_root
		)
		
		try:
			await self.json_rpc_client.check_health()
			CustomMCPServer.__log__("Checked json-rpc service", 'debug')
			
			yield {"json_rpc_client": self.json_rpc_client}
		finally:
			if self.json_rpc_client:
				await self.json_rpc_client.close()
				CustomMCPServer.__log__("Closed json-rpc connection", 'debug')
	
	def __register_handlers(self):

		@self.server.list_tools()
		async def handle_list_tools()->List[types.Tool]:
			ctx = self.server.request_context
			json_rpc_client: ClientJsonRPC = ctx.lifespan_context["json_rpc_client"]
			self.server.list_tools()(json_rpc_client.list_tools)
			
			try:
				tools = await json_rpc_client.list_tools()

				return tools
			except Exception as e:
				CustomMCPServer.__log__(f"Error gettering tools list: {e}", 'error')
				return []
		
		@self.server.call_tool()
		async def handle_call_tool(name: str, arguments: Dict[str, Any])->List[types.TextContent]:

			ctx = self.server.request_context
			json_rpc_client: ClientJsonRPC = ctx.lifespan_context["json_rpc_client"]
			
			try:
				CustomMCPServer.__log__(f"Call tools: {name} with args: {arguments}", 'debug')
				result = await json_rpc_client.call_tool(name, arguments)
				
				if result.isError:
					CustomMCPServer.__log__(f"Error call tool {name}", 'error')
				
				return result.content
			except Exception as e:
				CustomMCPServer.__log__(f"Error call tool {name}: {e}", 'error')
				return [types.TextContent(
					type="text",
					text=f"Error call tool: {str(e)}"
				)]
		
		@self.server.list_resources()
		async def handle_list_resources()->List[types.Resource]:

			ctx = self.server.request_context
			json_rpc_client:ClientJsonRPC = ctx.lifespan_context["json_rpc_client"]
			
			try:
				resources = await json_rpc_client.list_resources()

				return resources
			except Exception as e:
				CustomMCPServer.__log__(f"Error gettering resources: {e}", 'error')
				return []
		
		@self.server.read_resource()
		async def handle_read_resource(uri: str)->types.ReadResourceResult:

			ctx = self.server.request_context
			json_rpc_client:ClientJsonRPC = ctx.lifespan_context["json_rpc_client"]
			
			try:
				CustomMCPServer.__log__(f"Reading resource: {uri}", 'debug')
				
				result = await json_rpc_client.read_resource(uri)
				
				return result
			except Exception as e:
				CustomMCPServer.__log__(f"Error with reading resource {uri}: {e}", 'error')

				return types.ReadResourceResult(
					contents=[
						types.TextResourceContents(
							uri=uri,
							mimeType="text/plain",
							text=f"Error with reading resource: {str(e)}"
						)
					]
				)
		
		@self.server.list_prompts()
		async def handle_list_prompts()->List[types.Prompt]:

			ctx = self.server.request_context
			json_rpc_client:ClientJsonRPC = ctx.lifespan_context["json_rpc_client"]
			
			try:
				prompts = await json_rpc_client.list_prompts()
				
				return prompts
			except Exception as e:
				CustomMCPServer.__log__(f"Error gettering list prompt: {e}", 'error')
				return []
		
		@self.server.get_prompt()
		async def handle_get_prompt(name: str, arguments: Optional[Dict[str, str]] = None)->types.GetPromptResult:
			ctx = self.server.request_context
			json_rpc_client:ClientJsonRPC = ctx.lifespan_context["json_rpc_client"]
			
			try:
				CustomMCPServer.__log__(f"Get prompt: {name} with args: {arguments}", 'debug')
				
				result = await json_rpc_client.get_prompt(name, arguments)
				
				return result
			except Exception as e:
				CustomMCPServer.__log__(f"Error gettering list prompt {name}: {e}", 'error')
				return types.GetPromptResult(
					description=f"Error gettering list prompt: {str(e)}",
					messages=[]
				)
	
	def get_capabilities(self)->Dict[str, Any]:

		return {
			"tools": {
				"listChanged": True
			},
			"resources": {
				"subscribe": True,
				"listChanged": True
			},
			"prompts": {
				"listChanged": True
			},
			"logging": {}
		}
	
	def get_initialization_options(self)->InitializationOptions:

		return InitializationOptions(
			server_name=self.config.service_name,
			server_version=self.config.server_version,
			capabilities=self.server.get_capabilities(
				notification_options=NotificationOptions(
					tools_changed=True,
					resources_changed=True,
					prompts_changed=True
				),
				experimental_capabilities={}
			)
		)