# Python Standard Library imports
from collections import defaultdict

# Third-party Library imports
# Dependency Injection imports
from dependency_injector import containers, providers
# FastAPI imports
from fastapi.security import OAuth2PasswordBearer

# Custom Library imports
# Logging related
from app.logging import ApplicationLogging
# Configuration related
from config import get_settings
# LLM related
from sc2editor.llm import SC2EditorLLM


class Container(containers.DeclarativeContainer):
    """Dependency Injection Container for the application."""

    wiring_config = containers.WiringConfiguration(
                                                    modules=[
                                                                "__main__",
                                                                "app.main",
                                                                "app.core.auth",
                                                                "app.core.security",
                                                                "app.api.routers.auth",
                                                                "app.api.routers.conversations",
                                                                "app.api.routers.chat",
                                                                "app.api.routers.health",
                                                                "app.services.chat_service",
                                                                "app.utils.conversations",
                                                            ]
                                                )

    # Logger provider
    app_logging = providers.Singleton(ApplicationLogging)

    # OAuth2 security scheme provider
    oauth2_scheme = providers.Singleton(OAuth2PasswordBearer, tokenUrl="token", auto_error=False)

    # Configuration provider
    config = providers.Configuration(pydantic_settings=[get_settings()])
    # LLM provider
    llm = providers.Singleton(
        SC2EditorLLM,
        neo4j_uri=config.neo4j_uri.provided,
        neo4j_username=config.neo4j_username.provided,
        neo4j_password=config.neo4j_password.provided,
        model=config.llm.model.provided,
        embedding=config.llm.embedding.provided,
        maximum_information_acquisition_rate=config.llm.maximum_information_acquisition_rate.provided,
        maximum_retriever_attempts=config.llm.maximum_retriever_attempts.provided,
        timeout=config.llm.timeout.provided
    )

    # Conversations storage provider
    conversations = providers.Singleton(
        defaultdict,
        list
    )