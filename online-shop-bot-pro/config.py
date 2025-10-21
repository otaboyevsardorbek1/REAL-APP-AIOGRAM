import os
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

# .env faylni yuklash
load_dotenv()


class LogSettings(BaseModel):
    file: str
    max_size_mb: int
    to_console: bool = True
    status: bool = True


class WebhookSettings(BaseModel):
    enabled: bool
    host: str
    path: str
    port: int
    ssl_cert: str
    ssl_key: str


class DBSettings(BaseModel):
    mode: str  # sqlite yoki postgres
    sqlite_path: str
    pg_user: str
    pg_password: str
    pg_host: str
    pg_port: int
    pg_name: str


class Settings(BaseModel):
    # BOT
    token: str
    username: str
    admins_id: List[int]
    admins_username: List[str]

    # KANAL
    channel_id: int
    channel_url: str
    channel_name: str
    channel_username: str

    # GURUH
    group_id: int
    group_url: str
    group_name: str
    group_username: str
    group_invite_link: str

    # TIZIM
    debug: bool
    env: str

    # ICHKI CONFIGLAR
    log: LogSettings
    webhook: WebhookSettings
    db: DBSettings

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            # Bot
            token=os.getenv("BOT_TOKEN"),
            username=os.getenv("BOT_USERNAME"),
            admins_id=[
                int(i) for i in os.getenv("BOT_ADMINS_ID", "").split(",") if i.strip().isdigit()
            ],
            admins_username=[
                i.strip() for i in os.getenv("BOT_ADMINS_USERNAME", "").split(",") if i.strip()
            ],

            # Kanal
            channel_id=int(os.getenv("CHANNEL_ID")),
            channel_url=os.getenv("CHANNEL_URL"),
            channel_name=os.getenv("CHANNEL_NAME"),
            channel_username=os.getenv("CHANNEL_USERNAME"),

            # Guruh
            group_id=int(os.getenv("GROUP_ID")),
            group_url=os.getenv("GROUP_URL"),
            group_name=os.getenv("GROUP_NAME"),
            group_username=os.getenv("GROUP_USERNAME"),
            group_invite_link=os.getenv("GROUP_INVITE_LINK"),

            # Debug / Env
            debug=os.getenv("DEBUG", "True").lower() == "true",
            env=os.getenv("ENV", "dev"),

            log=LogSettings(
            file=os.getenv("LOG_FILE", "bot.log"),
            max_size_mb=int(os.getenv("LOG_MAX_SIZE_MB", 32)),
            to_console=os.getenv("LOG_TO_CONSOLE", "true").lower() == "true",
            status=os.getenv("LOG_STATUS", "true").lower() == "true",
            ),

            # Webhook
            webhook=WebhookSettings(
                enabled=os.getenv("WEBHOOK_ENABLED", "false").lower() == "true",
                host=os.getenv("WEBHOOK_HOST", ""),
                path=os.getenv("WEBHOOK_PATH", ""),
                port=int(os.getenv("WEBHOOK_PORT", 8443)),
                ssl_cert=os.getenv("WEBHOOK_SSL_CERT", ""),
                ssl_key=os.getenv("WEBHOOK_SSL_KEY", "")
            ),

            # Database
            db=DBSettings(
                mode=os.getenv("DB_MODE", "sqlite"),
                sqlite_path=os.getenv("DB_SQLITE_PATH", "bot.db"),
                pg_user=os.getenv("DB_PG_USER", ""),
                pg_password=os.getenv("DB_PG_PASSWORD", ""),
                pg_host=os.getenv("DB_PG_HOST", ""),
                pg_port=int(os.getenv("DB_PG_PORT", 5432)),
                pg_name=os.getenv("DB_PG_NAME", "")
            )
        )


# Global settings obyekt
config = Settings.from_env()
