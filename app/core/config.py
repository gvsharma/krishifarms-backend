from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "KrishiFarms CRM"
    app_env: str = "development"
    debug: bool = False
    secret_key: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    database_url: str

    cache_provider: str = "memory"
    cache_ttl_seconds: int = 300
    redis_url: str | None = None

    aws_region: str = "ap-south-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    s3_bucket_name: str = "krishifarms-documents"
    s3_presigned_url_expire_seconds: int = 900

    cors_origins: str = "http://localhost:3000"

    default_org_name: str = "Krishi Farms"
    default_owner_email: str = "owner@krishifarms.local"
    default_owner_password: str = "ChangeMe123!"
    default_owner_name: str = "Owner"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
