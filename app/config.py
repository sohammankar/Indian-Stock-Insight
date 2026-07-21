from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./dev.db"
    anthropic_api_key: str = ""
    groq_api_key: str = ""
    llm_provider: str = "groq"  # "groq" (free) or "anthropic" (paid)

    class Config:
        env_file = ".env"


settings = Settings()
