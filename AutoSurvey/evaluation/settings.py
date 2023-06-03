from pydantic import BaseSettings


class Settings(BaseSettings):
    openai_key: str
    model: str = "gpt-3.5-turbo"
    temperature: float = 1.0
    max_tokens: int = 1
    top_p: float = 1.0
    n: int = 20

    class Config:
        env_file = ".env"

    
settings = Settings()