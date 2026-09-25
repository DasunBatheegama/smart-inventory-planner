from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "InventIQ API"
    database_url: str
    frontend_url: str = "http://localhost:3000"
    alert_overstock_days_threshold: int = 90
    alert_slow_moving_avg_daily_demand_threshold: float = 0.5
    alert_slow_moving_min_stock: int = 25
    alert_forecast_anomaly_enabled: bool = False
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-120b"
    groq_timeout_seconds: float = 30.0
    groq_base_url: str = "https://api.groq.com/openai/v1"

    class Config:
        env_file = ".env"

settings = Settings()
