from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import find_dotenv


class Settings(BaseSettings):
    APP_ENV: str = "dev"
    LOG_LEVEL: str = "DEBUG"

    SESSION_POOL_SIZE: int = 1
    MAX_SCRAPE_DELAY: float = 1800.0  # 30 minutes
    DQ_MAX_SIZE: int = 1000  # max size of the deque for memory database
    REDIS_RECORD_EXPIRY_SECONDS: int = 3456000 # 40 days (40*24*60*60)
    CONCURRENCY: int = 1
    TASK_INTERVAL_SECONDS: float = 1.0
    START_OFFSET_SECONDS: float = 60.0

    DB_TYPE: Literal["memory", "redis", "sqlite"] = "memory"
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASS: str | None = None
    DB_HOST: str | None = "localhost"
    DB_PORT: int | None = 6379
    DB_PATH: str | None = ".zenx/data.db"

    PROXY: str | None = None

    SYNOPTIC_GRPC_SERVER_URI: str = "ingress.opticfeeds.com"
    SYNOPTIC_GRPC_TOKEN: str | None = None
    SYNOPTIC_GRPC_ID: str | None = None
    # enterprise
    SYNOPTIC_ENTERPRISE_USEAST1_GRPC_SERVER_URI: str | None = "us-east-1.enterprise.synoptic.com:50051"
    SYNOPTIC_ENTERPRISE_EUCENTRAL1_GRPC_SERVER_URI: str | None = "eu-central-1.enterprise.synoptic.com:50051"
    SYNOPTIC_ENTERPRISE_EUWEST2_GRPC_SERVER_URI: str | None = "eu-west-2.enterprise.synoptic.com:50051"
    SYNOPTIC_ENTERPRISE_USEAST1CHI2A_GRPC_SERVER_URI: str | None = "us-east-1-chi-2a.enterprise.synoptic.com:50051"
    SYNOPTIC_ENTERPRISE_USEAST1NYC2A_GRPC_SERVER_URI: str | None = "us-east-1-nyc-2a.enterprise.synoptic.com:50051"
    SYNOPTIC_ENTERPRISE_APNORTHEAST1_GRPC_SERVER_URI: str | None = "ap-northeast-1.enterprise.synoptic.com:50051"
    SYNOPTIC_ENTERPRISE_GRPC_TOKEN: str | None = None
    SYNOPTIC_ENTERPRISE_GRPC_ID: str | None = None

    SYNOPTIC_DISCORD_WEBHOOK: str | None = None

    SYNOPTIC_WS_API_KEY: str | None = None
    SYNOPTIC_WS_STREAM_ID: str | None = None
    SYNOPTIC_FREE_WS_API_KEY: str | None = None
    SYNOPTIC_FREE_WS_STREAM_ID: str | None = None

    MONITOR_ITXP_SOCKET_PATH: str | None = "/tmp/itxpmonitor.sock"
    MONITOR_ITXP_TRIGGER_STATUS_CODE: int | None = 200
    MONITORING_ENABLED: bool = False

    model_config = SettingsConfigDict(env_file=find_dotenv(".env"), extra="allow", case_sensitive=True)

settings = Settings()
