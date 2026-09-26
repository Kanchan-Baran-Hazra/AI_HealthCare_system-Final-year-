from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    ENV: str = "devlopment"
    DEBUG: bool = False

    ADMIN_NAME:str
    ADMIN_EMAIL:str

    DATABASE_URL:str
    REDIS_URL:str

    SALT:str
    SECRET_KEY:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    REFRESH_TOKEN_EXPIRE_DAY:int


    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str

    REACT_URI:str
    BACKEND_URI:str

    GOOGLE_CLIENT_ID:str
    GOOGLE_CLIENT_SECRET:str
    GOOGLE_REDIRECT_URI:str

    GITHUB_CLIENT_ID:str
    GITHUB_CLIENT_SECRET:str
    GITHUB_REDIRECT_URI:str


    model_config=SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

Config=Settings()