from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "ollama"
    model_name: str = "gpt-oss:latest"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"

    # OpenAI
    openai_api_key: str = ""

    # Anthropic
    anthropic_api_key: str = ""

    # Azure OpenAI
    azure_api_key: str = ""
    azure_api_base: str = ""
    azure_api_version: str = "2024-08-01-preview"

    # Server
    host: str = "0.0.0.0"
    port: int = 8100

    # Database
    database_url: str = "sqlite:///./query_builder.db"

    # Qdrant
    qdrant_url: str = "https://vector.cyberglobes.ai"
    qdrant_api_key: str = ""
    qdrant_collection: str = "cg_data_sources_dev"

    # Logging
    log_level: str = "info"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def litellm_model(self) -> str:
        """Return the model string in litellm format."""
        if self.llm_provider == "ollama":
            return f"ollama/{self.model_name}"
        elif self.llm_provider == "azure":
            return f"azure/{self.model_name}"
        return self.model_name

    @property
    def litellm_api_base(self) -> str | None:
        """Return the API base URL for litellm."""
        if self.llm_provider == "ollama":
            return self.ollama_base_url
        if self.llm_provider == "azure":
            return self.azure_api_base or None
        return None

    @property
    def litellm_extra_kwargs(self) -> dict:
        """Return extra kwargs for litellm based on provider."""
        if self.llm_provider == "azure":
            return {
                "api_key": self.azure_api_key,
                "api_version": self.azure_api_version,
            }
        return {}


settings = Settings()
