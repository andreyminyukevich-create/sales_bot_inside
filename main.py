import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
from database import init_db
from handlers import client, admin


async def main():
    """Главная функция запуска бота"""
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Проверка обязательных переменных
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен! Проверьте переменные окружения в Railway.")
        return
    
    if not config.DATABASE_URL:
        logger.error("DATABASE_URL не установлен! Проверьте переменные окружения в Railway.")
        return
    
    # Инициализация базы данных
    logger.info("Инициализация базы данных...")
    try:
        engine, SessionLocal = init_db(config.DATABASE_URL)
        logger.info("База данных готова!")
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        return
    
    # Создание бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Передаём SessionLocal в диспетчер (чтобы handlers могли использовать)
    dp["db_session"] = SessionLocal
    
    # Регистрация handlers
    dp.include_router(client.router)
    dp.include_router(admin.router)
    
    logger.info("Бот запущен!")
    logger.info(f"Admin chat ID: {config.ADMIN_CHAT_ID}")
    logger.info(f"Owner chat ID: {config.OWNER_CHAT_ID}")
    
    # Запуск polling
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
