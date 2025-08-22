from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  database_hostname: str
  database_port: int
  database_password: str
  database_name: str
  database_username: str
  secret_key: str
  algorithm: str
  access_token_expire_minutes: int
  panel_key: str
  front_url: str

  # Pydantic v2 CONFIG (Auto fills the data from .env)
  model_config = SettingsConfigDict(env_file = ".env")

settings = Settings()

