from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ShipTrack"
    SECRET_KEY: str = Field(..., json_schema_extra={"env": "SECRET_KEY"})
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = Field(..., json_schema_extra={"env": "DATABASE_URL"})
    CORS_ORIGINS: str = Field(default="http://localhost:3000", json_schema_extra={"env": "CORS_ORIGINS"})

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

config: Config = Config()

# Keep backward compatibility
settings = config
