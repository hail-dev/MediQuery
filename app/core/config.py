from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    API_KEY: str

    # OpenAI
    OPENAI_API_KEY: str

    # Database
    DB_URL: str

    # AWS S3
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str

    # RAG Settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RETRIEVER_TOP_K: int = 5

    class Config:
        env_file = ".env"

settings = Settings()