"""Клиент для взаимодействия с 1С."""

import json
import logging
from typing import Any, Dict, List, Optional
import httpx
from mcp import types


logger = logging.getLogger(__name__)


class ClientJsonRPC:
	def __init__(self, base_url: str, username: str, password: str, service_root: str = "mcp"):
		self.base_url = base_url.rstrip('/')
		self.service_root = service_root.strip('/')
		self.auth = httpx.BasicAuth(username, password) if username and password else None
		self.client = httpx.AsyncClient(
			auth=self.auth,
			timeout=30.0,
			headers={"Content-Type": "application/json"}
		)
		
		self.service_base_url = f"{self.base_url}/{self.service_root}"
		logger.debug(f"Base URL Json-rpc service: {self.service_base_url}")
	
	async def check_health(self) -> bool:
		try:
			url = f"{self.service_base_url}/health"
			logger.debug(f"check health: {url}")
			response = await self.client.get(url)
			response.raise_for_status()

			try:
				response_json = response.json()
				if response_json.get("status") == "ok":
					logger.debug("Json rpc service is ok")
					return True
				else:
					logger.warning(f"Json rpc Service return health check with status: {response_json}")
					raise httpx.HTTPStatusError(f"Json rpc service reported not healthy: {response_json}", request=response.request, response=response)
			except json.JSONDecodeError as e:
				logger.error(f"Error parsing JSON response health-check Json-rpc service: {response.text}")
				raise httpx.HTTPStatusError(f"Invalid JSON response from  health check: {e}", request=response.request, response=response)

		except httpx.HTTPError as e:
			logger.error(f"Error HTTP check Json-rpc service: {e}")
			raise
	
	async def call_rpc(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
		try:
			url = f"{self.service_base_url}/rpc"
			
			rpc_request = {
				"jsonrpc": "2.0",
				"id": 1,
				"method": method,
				"params": params or {}
			}
			
			logger.debug(f"JSON-RPC request: {rpc_request}")
			
			response = await self.client.post(url, json=rpc_request)
			response.raise_for_status()
			
			rpc_response = response.json()
			logger.debug(f"JSON-RPC response: {rpc_response}")
			
			if "error" in rpc_response:
				error = rpc_response["error"]
				raise Exception(f"JSON-RPC error {error.get('code', 'unknown')}: {error.get('message', 'Unknown error')}")
			
			return rpc_response.get("result", {})
			
		except httpx.HTTPError as e:
			logger.error(f"Error HTTP when call RPC: {e}")
			raise
		except json.JSONDecodeError as e:
			logger.error(f"Error parsing JSON response RPC: {e}")
			raise
	
	async def list_tools(self) -> List[types.Tool]:
		result = await self.call_rpc("tools/list")
		tools_data = result.get("tools", [])
		
		tools = []
		for tool_data in tools_data:
			tool = types.Tool(
				name=tool_data["name"],
				description=tool_data.get("description", ""),
				inputSchema=tool_data.get("inputSchema", {})
			)
			tools.append(tool)
		
		return tools
	
	async def call_tool(self, name: str, arguments: Dict[str, Any]) -> types.CallToolResult:

		result = await self.call_rpc("tools/call", {
			"name": name,
			"arguments": arguments
		})
		
		content = []
		if "content" in result:
			for item in result["content"]:
				content_type = item.get("type")
				
				if content_type == "text":
					content.append(types.TextContent(
						type="text",
						text=item.get("text", "")
					))
				
				elif content_type == "image":
					content.append(types.ImageContent(
						type="image",
						data=item.get("data", ""),
						mimeType=item.get("mimeType", "image/png")
					))
				
				else:
					logger.warning(f"Unknow type content: {content_type}, proccess as text")
					content.append(types.TextContent(
						type="text",
						text=str(item.get("text", item))
					))
		
		return types.CallToolResult(
			content=content,
			isError=result.get("isError", False)
		)
	
	async def list_resources(self) -> List[types.Resource]:
		result = await self.call_rpc("resources/list")
		resources_data = result.get("resources", [])
		
		resources = []
		for resource_data in resources_data:
			resource = types.Resource(
				uri=resource_data["uri"],
				name=resource_data.get("name", ""),
				description=resource_data.get("description", ""),
				mimeType=resource_data.get("mimeType")
			)
			resources.append(resource)
		
		return resources
	
	async def read_resource(self, uri: str) -> types.ReadResourceResult:
		result = await self.call_rpc("resources/read", {"uri": uri})

		contents = []
		if "contents" in result:
			for item in result["contents"]:
				content_type = item.get("type")
				
				if content_type == "text":
					contents.append(types.TextResourceContents(
						uri=uri,
						mimeType=item.get("mimeType", "text/plain"),
						text=item.get("text", "")
					))
				
				elif content_type == "blob":
					contents.append(types.BlobResourceContents(
						uri=uri,
						mimeType=item.get("mimeType", "application/octet-stream"),
						blob=item.get("blob", "")
					))
				
				else:
					logger.warning(f"Unknow type resource: {content_type}, process as text")
					
					text_content = ""
					if "text" in item:
						text_content = str(item["text"])
					elif "data" in item:
						text_content = str(item["data"])
					elif "content" in item:
						text_content = str(item["content"])
					else:
						text_content = f"Unknow type resource '{content_type}': {json.dumps(item, ensure_ascii=False)}"
					
					contents.append(types.TextResourceContents(
						uri=uri,
						mimeType=item.get("mimeType", "text/plain"),
						text=text_content
					))
		
		return types.ReadResourceResult(contents=contents)
	
	async def list_prompts(self) -> List[types.Prompt]:
		result = await self.call_rpc("prompts/list")
		prompts_data = result.get("prompts", [])
		
		prompts = []
		for prompt_data in prompts_data:
			arguments = []
			if "arguments" in prompt_data:
				for arg_data in prompt_data["arguments"]:
					arguments.append(types.PromptArgument(
						name=arg_data["name"],
						description=arg_data.get("description", ""),
						required=arg_data.get("required", False)
					))
			
			prompt = types.Prompt(
				name=prompt_data["name"],
				description=prompt_data.get("description", ""),
				arguments=arguments
			)
			prompts.append(prompt)
		
		return prompts
	
	async def get_prompt(self, name: str, arguments: Optional[Dict[str, str]] = None) -> types.GetPromptResult:
		result = await self.call_rpc("prompts/get", {
			"name": name,
			"arguments": arguments or {}
		})
		
		messages = []
		if "messages" in result:
			for msg_data in result["messages"]:
				content = types.TextContent(
					type="text",
					text=msg_data.get("content", {}).get("text", "")
				)
				
				message = types.PromptMessage(
					role=msg_data.get("role", "user"),
					content=content
				)
				messages.append(message)
		
		return types.GetPromptResult(
			description=result.get("description", ""),
			messages=messages
		)
	
	async def close(self):
		await self.client.aclose() 