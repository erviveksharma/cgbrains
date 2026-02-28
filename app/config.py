from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "ollama"
    model_name: str = "gpt-oss:latest"
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8100

    # Database
    database_url: str = "sqlite:///./query_builder.db"

    # Logging
    log_level: str = "info"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def litellm_model(self) -> str:
        """Return the model string in litellm format."""
        if self.llm_provider == "ollama":
            return f"ollama/{self.model_name}"
        elif self.llm_provider == "openai":
            return self.model_name
        elif self.llm_provider == "anthropic":
            return self.model_name
        return self.model_name

    @property
    def litellm_api_base(self) -> str | None:
        """Return the API base URL for litellm."""
        if self.llm_provider == "ollama":
            return self.ollama_base_url
        return None


settings = Settings()
