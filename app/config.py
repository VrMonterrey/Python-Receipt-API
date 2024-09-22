from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URL_TEST: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
