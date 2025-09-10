"""Configuration management for the Ultimate Trading Solution."""

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, Field, validator


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    url: str = Field(default="sqlite:///./trading.db", env="DATABASE_URL")
    echo: bool = Field(default=False, env="DATABASE_ECHO")
    pool_size: int = Field(default=5, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")

    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Redis configuration settings."""

    url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")

    class Config:
        env_prefix = "REDIS_"


class APISettings(BaseSettings):
    """API configuration settings."""

    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    workers: int = Field(default=1, env="API_WORKERS")
    reload: bool = Field(default=False, env="API_RELOAD")
    cors_origins: List[str] = Field(default=["*"], env="API_CORS_ORIGINS")

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_prefix = "API_"


class TradingSettings(BaseSettings):
    """Trading configuration settings."""

    default_timeframe: str = Field(default="1h", env="TRADING_DEFAULT_TIMEFRAME")
    max_positions: int = Field(default=10, env="TRADING_MAX_POSITIONS")
    risk_per_trade: float = Field(default=0.02, env="TRADING_RISK_PER_TRADE")
    stop_loss_pct: float = Field(default=0.05, env="TRADING_STOP_LOSS_PCT")
    take_profit_pct: float = Field(default=0.10, env="TRADING_TAKE_PROFIT_PCT")

    @validator("risk_per_trade", "stop_loss_pct", "take_profit_pct")
    def validate_percentages(cls, v: float) -> float:
        """Validate that percentages are between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Percentage must be between 0 and 1")
        return v

    class Config:
        env_prefix = "TRADING_"


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""

    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT",
    )
    file_path: Optional[str] = Field(default=None, env="LOG_FILE_PATH")
    max_file_size: int = Field(default=10485760, env="LOG_MAX_FILE_SIZE")  # 10MB
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")

    @validator("level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    class Config:
        env_prefix = "LOG_"


class Settings(BaseSettings):
    """Main application settings."""

    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")

    # API Keys (for external services)
    alpha_vantage_key: Optional[str] = Field(default=None, env="ALPHA_VANTAGE_KEY")
    binance_api_key: Optional[str] = Field(default=None, env="BINANCE_API_KEY")
    binance_secret_key: Optional[str] = Field(default=None, env="BINANCE_SECRET_KEY")

    # Sub-settings
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    api: APISettings = APISettings()
    trading: TradingSettings = TradingSettings()
    logging: LoggingSettings = LoggingSettings()

    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment setting."""
        valid_environments = ["development", "staging", "production"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Environment must be one of {valid_environments}")
        return v.lower()

    @validator("debug", pre=True)
    def parse_debug(cls, v: Any) -> bool:
        """Parse debug setting from string or boolean."""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()
