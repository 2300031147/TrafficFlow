import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class ServerSettings(BaseSettings):
    database_url: str = "postgres://urban_admin:changeme_dev_only@localhost:5432/urbanflow"
    database_url_sync: str = "postgresql://urban_admin:changeme_dev_only@localhost:5432/urbanflow"
    redis_url: str = "redis://:changeme_dev_only@localhost:6379/0"  # SEC-4/9: password required
    
    jwt_secret_key: str = "development-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    bcrypt_rounds: int = 12
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    environment: str = "development"
    log_level: str = "INFO"
    superadmin_email: str = "admin@urbanflow.local"
    
    api_port: int = 8000
    dashboard_port: int = 3000
    websocket_interval_seconds: int = 2
    health_check_interval_seconds: int = 60
    stream_port: int = 8080  # override via STREAM_PORT env var (pydantic-settings handles it)
    
    retrain_lstm_cron: str = "0 3 * * *"
    retrain_rl_cron: str = "0 4 * * *"
    
    auth_lockout_attempts: int = 5
    auth_lockout_minutes: int = 15
    model_storage_path: str = "/var/lib/urbanflow/models"
    
    ingest_rate_limit_per_minute: int = 60
    api_rate_limit_per_minute: int = 120
    auth_rate_limit_per_minute: int = 10
    global_rate_limit_per_minute: int = 300

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

settings = ServerSettings()

