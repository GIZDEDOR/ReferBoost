import asyncio

from aiogram import Bot, Dispatcher

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.handlers import setup_routers
from bot.middlewares import DBSessionMiddleware

from db import Base
from config_reader import config

bot = Bot(config.BOT_TOKEN.get_secret_value())
dp = Dispatcher()

_engine = create_async_engine(config.DB_URL.get_secret_value())
_sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)

dp.update.middleware(DBSessionMiddleware(_sessionmaker))
dp.include_router(setup_routers())

dp.startup()
async def on_startup() -> None:
    await bot.delete_webhook(True)

    async with _engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


@dp.shutdown()
async def on_shutdown(session: AsyncSession) -> None: 
    await session.close()


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))    