from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import config

# 🔧 Dinamik ravishda connection stringni yaratish
if config.db.mode == "sqlite":
    DATABASE_URL = f"sqlite:///{config.db.sqlite_path}"
elif config.db.mode == "postgres":
    DATABASE_URL = (
        f"postgresql://{config.db.pg_user}:{config.db.pg_password}"
        f"@{config.db.pg_host}:{config.db.pg_port}/{config.db.pg_name}"
    )
else:
    raise ValueError("DB_MODE noto‘g‘ri! Faqat 'sqlite' yoki 'postgres' bo‘lishi mumkin.")

# 🔌 Engine va Session
engine = create_engine(
    DATABASE_URL,
    echo=config.debug,
    future=True,
    connect_args={"check_same_thread": False} if config.db.mode == "sqlite" else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

# 📦 Declarative Base
Base = declarative_base()

# 🧱 Ma'lumotlar bazasini boshlash
async def init_db():
    from . import models  # model fayllaringizni shu yerda import qiling
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized successfully.")
