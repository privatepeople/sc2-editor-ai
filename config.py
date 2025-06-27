# Python Standard Library imports
from typing import Union
from functools import lru_cache

# Third-party Library imports
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Custom Library imports
from utils import load_config


class LLMConfig(BaseModel):
    """LLM configuration settings"""
    model: str = Field(default="gemini-2.0-flash", description="Gemini LLM Model")
    embedding: str = Field(default="models/text-embedding-004", description="Gemini Embedding Model")
    maximum_information_acquisition_rate: Union[int, float] = Field(default=0.15, ge=0.0, le=1.0, description="Maximum data rate that can be retrieved by the retriever")
    maximum_retriever_attempts: int = Field(default=2, ge=1, description="Maximum number of retriever attempts")


class FastAPIConfig(BaseModel):
    """FastAPI configuration settings"""
    api_limit: int = Field(default=1, ge=1, description="API limit per minutes")
    api_limit_cooldown: int = Field(default=60, ge=1, description="API limit cooldown(seconds)")
    session_timeout: int = Field(default=60, ge=1, description="Session timeout(minutes)")
    session_timeout_check_period: int = Field(default=60, ge=1, description="Check period(seconds)")


class Settings(BaseSettings):
    """Main settings class that loads from .env and config.yaml"""
    
    model_config = SettingsConfigDict(
                                        env_file=".env",
                                        env_file_encoding="utf-8",
                                        case_sensitive=False,
                                        extra="allow"
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
        self.llm = LLMConfig(**yaml_data['llm'])
        self.fastapi = FastAPIConfig(**yaml_data['fastapi'])


# Activate Environment variables
load_dotenv()
# Create a global settings instance
settings = Settings()


# Helper function to get settings (useful for dependency injection)
@lru_cache
def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings


if __name__ == "__main__":
    print("Configuration loaded successfully!")
    print(f"LLM Model: {settings.llm.model}")
    print(f"Embedding Model: {settings.llm.embedding}")
    print(f"Max Info Acquisition Rate: {settings.llm.maximum_information_acquisition_rate}")
    print(f"Max Retriever Attempts: {settings.llm.maximum_retriever_attempts}")
    print(f"API Limit: {settings.fastapi.api_limit} minutes")
    print(f"Session Timeout: {settings.fastapi.session_timeout} minutes")
    print(f"Session Check Period: {settings.fastapi.session_timeout_check_period} seconds")