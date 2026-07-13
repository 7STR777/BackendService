from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str = ""
    ALGORITHM: str = ""
    DB_USER: str = ""
    DB_HOST: str = ""
    DB_PORT: int = 5432
    DB_NAME: str = ""
    DB_PASS: str = ""
    BASE_URL: str = ""

    @property
    def DATABASE_URL_asyncpg(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

#.env вида:
# SECRET_KEY = КЛЮЧ
# ALGORITHM = HS256

# DB_NAME=НАЗВАНИЕ
# DB_HOST=localhost
# DB_PORT=5432
# DB_PASS=ПАРОЛЬ
# DB_USER=postgres

# BASE_URL = "127.0.0.1:8000"