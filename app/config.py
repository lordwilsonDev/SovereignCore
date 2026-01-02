from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SovereignCore"
    SECRET_KEY: str = "sovereign_core_secret_key_change_me_in_production"
    DATABASE_URL: str = "sqlite:///./sovereign.db"
    
    # Pydantic V2 Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

settings = Settings()
