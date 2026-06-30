# ============================================================
# ТОЧКА ВХОДА В ПРОГРАММУ
# Запускает парсинг всех моделей из списка
# ============================================================
from dotenv import load_dotenv
import os
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.memory import MemoryStorage

from src.logger import logger
from src.config import MODELS_TO_PARSE
from app.handlers import router


load_dotenv()

TOKEN = os.getenv('TOKEN')
WORKER_URL = os.getenv('WORKER_URL')

# Проверка обязательных переменных
if not TOKEN:
    raise ValueError("❌ TOKEN не найден в .env файле!")
if not WORKER_URL:
    raise ValueError("❌ WORKER_URL не найден в .env файле!")


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================
async def main() -> None:
    """Главная функция: запускает парсинг и сохраняет результаты."""
    
    logger.info("=" * 60)
    logger.info("🚀 ЗАПУСК ПАРСЕРА")
    logger.info("=" * 60)
    logger.info(f"📦 Моделей: {len(MODELS_TO_PARSE)}")

    # Если WORKER_URL есть - используем прокси через сессию
    if WORKER_URL:
        logger.info(f"🌐 Используется прокси: {WORKER_URL}")

        # Создаем объект TelegramAPIServer с вашим прокси
        api_server = TelegramAPIServer.from_base(WORKER_URL)

        # Создаем сессию
        session = AiohttpSession(
            api=api_server
        )

        # Передаем сессию в Bot
        bot = Bot(
            token=TOKEN,
            default=DefaultBotProperties(
                parse_mode="HTML"
            ),
            session=session
        )
    else:
        # Без прокси
        logger.info("🌐 Прямое подключение (без прокси)")
        bot = Bot(
            token=TOKEN,
            default=DefaultBotProperties(parse_mode="HTML")
        )

    # Проверяем подключение к Telegram
    try:
        me = await bot.get_me()
        logger.info(f"✅ Бот подключен: @{me.username} (ID: {me.id})")
    except Exception as e:
        logger.error(f"❌ Не удалось подключиться к Telegram: {e}")
        logger.error("Проверьте интернет-соединение и доступ к api.telegram.org")
        return
    
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    dp.include_router(router)

    logger.info("🔄 Запуск поллинга...")
    try:
        await dp.start_polling(
            bot,
            skip_updates=True,  # Пропускаем старые обновления
            allowed_updates=["message", "callback_query"]  # Только нужные типы
        )
    except Exception as e:
        logger.error(f"❌ Ошибка поллинга: {e}")
    finally:
        await bot.session.close()
        logger.info("👋 Сессия закрыта")

# ============================================================
# ЗАПУСК ПРОГРАММЫ
# ============================================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")