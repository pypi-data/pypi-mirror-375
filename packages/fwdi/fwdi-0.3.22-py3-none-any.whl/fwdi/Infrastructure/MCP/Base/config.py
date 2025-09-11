from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
	host: str = Field(default="127.0.0.1", description="HOST")
	port: int = Field(default=8000, description="PORT")
	base_url: str = Field(description="Base URL")
	username: str = Field(description="User name")
	password: str = Field(description="Password")
	service_root: str = Field(default="mcp", description="Service root path")
	service_name: str = Field(default="Service Configuration Data Tools", description="Name MCP-service")
	server_version: str = Field(default="1.0.0", description="Verison MCP-service")
	log_level: str = Field(default="INFO", description="Log level")
	cors_origins: list[str] = Field(default=["*"], description="Разрешенные CORS origins")

	@staticmethod
	def get_config() -> 'Config':
		return Config() 