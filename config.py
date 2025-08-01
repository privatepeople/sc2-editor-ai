# Python Standard Library imports
from typing import Union
from functools import lru_cache

# Third-party Library imports
from dotenv import load_dotenv
from pydantic import BaseModel, Field, IPvAnyAddress
from pydantic_settings import BaseSettings, SettingsConfigDict

# Custom Library imports
from utils import load_config


class LLMConfig(BaseModel):
    """LLM configuration settings"""

    model: str = Field(default="gemini-2.0-flash", description="Gemini LLM Model")
    embedding: str = Field(
        default="models/text-embedding-004", description="Gemini Embedding Model"
    )
    maximum_information_acquisition_rate: Union[int, float] = Field(
        default=0.15,
        ge=0.0,
        le=1.0,
        description="Maximum data rate that can be retrieved by the retriever",
    )
    maximum_retriever_attempts: int = Field(
        default=2, ge=1, description="Maximum number of retriever attempts"
    )
    timeout: Union[int, float] = Field(
        default=30.0, ge=15.0, description="Timeout for LLM requests in seconds"
    )


class FastAPIConfig(BaseModel):
    """FastAPI configuration settings"""

    api_limit: int = Field(default=1, ge=1, description="API limit per minutes")
    conversation_timeout: int = Field(
        default=60, ge=1, description="Conversation timeout(minutes)"
    )
    conversation_timeout_period: int = Field(
        default=60, ge=1, description="Period to check conversation timeout(seconds)"
    )
    access_token_expire: int = Field(
        default=60, ge=1, description="Time left until ACCESS TOKEN expires(minutes)"
    )
    https_status: bool = Field(
        default=False,
        description="Boolean variable indicating whether to apply https or not",
    )


class Settings(BaseSettings):
    """Main settings class that loads from .env and config.yaml"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="allow"
    )

    google_api_key: str
    neo4j_uri: str
    neo4j_username: str
    neo4j_password: str
    admin_username: str
    admin_password: str
    jwt_secret_key: str
    algorithm: str
    uvicorn_host: IPvAnyAddress = Field(
        default="127.0.0.1", description="Uvicorn server host"
    )
    uvicorn_port: int = Field(
        default=8080, ge=1, le=65535, description="Uvicorn server port"
    )

    # Configuration sections
    llm: LLMConfig = Field(default_factory=LLMConfig)
    fastapi: FastAPIConfig = Field(default_factory=FastAPIConfig)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_config()

    def _load_config(self):
        """Load configuration from config.yaml file"""
        yaml_data = load_config()
        self.llm = LLMConfig(**yaml_data["llm"])
        self.fastapi = FastAPIConfig(**yaml_data["fastapi"])


# Activate Environment variables
load_dotenv()


# Helper function to get settings (useful for dependency injection)
@lru_cache
def get_settings() -> Settings:
    """Get the global settings instance"""
    return Settings()
