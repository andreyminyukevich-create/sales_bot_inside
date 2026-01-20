import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
from database import init_db

# Импорты handlers будем добавлять постепенно
# from handlers import client, admin, dialog


async def main():
    """Главная функция запуска бота"""
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Инициализация базы данных
    logger.info("Инициализация базы данных...")
    engine, SessionLocal = init_db(config.DATABASE_URL)
    logger.info("База данных готова!")
    
    # Создание бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Передаём SessionLocal в диспетчер (чтобы handlers могли использовать)
    dp["db_session"] = SessionLocal
    
    # Регистрация handlers (пока закомментировано, добавим позже)
    # from handlers import client, admin, dialog
    # dp.include_router(client.router)
    # dp.include_router(admin.router)
    # dp.include_router(dialog.router)
    
    logger.info("Бот запущен!")
    
    # Запуск polling
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
