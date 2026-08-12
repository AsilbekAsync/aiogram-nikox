import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from alembic import command
from alembic.config import Config

from config import BOT_TOKEN
from database.base import Base
from database.engine import engine
from handlers.start import router as start_router
from handlers.unknown import router as unknown_router
import models  # pyright: ignore[reportUnusedImport]
from states.storage import SQLAlchemyStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logging.getLogger("alembic").setLevel(logging.WARNING)

logger = logging.getLogger("bot")


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    await create_tables()

    bot = Bot(token=BOT_TOKEN)
    storage = SQLAlchemyStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(start_router)
    dp.include_router(unknown_router)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    run_migrations()
    asyncio.run(main())
