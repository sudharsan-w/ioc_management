import os
import pytz
from pytz.tzinfo import BaseTzInfo
from pydantic import field_validator
from pydantic_settings import BaseSettings

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


class Env(BaseSettings):
    DEV: bool
    APP_MONGO_URL: str
    APP_DB_NAME: str
    API_KEY: str
    DEFAULT_TIME_ZONE: BaseTzInfo

    @field_validator("DEFAULT_TIME_ZONE", mode="before")
    def validate_time_zone(cls, value: str) -> BaseTzInfo:
        try:
            return pytz.timezone(value)
        except Exception:
            raise ValueError(f"Invalid time zone: {value}")

    class Config:
        env_file = env_path
        env_file_encoding = "utf-8"
