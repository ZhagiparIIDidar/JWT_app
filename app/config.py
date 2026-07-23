from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent


class AuthJWT(BaseModel):
    PRIVATE_KEY_PATH: Path = BASE_DIR / "certs" / "private_key_jwt.pem"
    PUBLIC_KEY_PATH: Path = BASE_DIR / "certs" / "private_key_jwt.pem"
    ALGORITHM: str = "RS256"
    access_token_expire_minutes: int = 1
    refresh_token_expire_days: int = 2


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    # @property
    # def DATABASE_URL_asyncpg(self):
    #     return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    #
    # @property
    # def DATABASE_URL_psycopg(self):
    #     return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_asyncpg(self):
        return f"sqlite+aiosqlite:///{self.DB_NAME}.db"

    @property
    def DATABASE_URL_psycopg(self):
        return f"sqlite:///{self.DB_NAME}.db"

    auth_jwt: AuthJWT = AuthJWT()

    model_config = SettingsConfigDict(
        env_file=".env.example",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
