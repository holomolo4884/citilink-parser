from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboars as kb
from src.config import MODELS_TO_PARSE, DELAYS, OUTPUT
from src.logger import logger
from src.parser import parse_by_search
from src.utils import save_results, save_as_csv, print_summary

from dotenv import load_dotenv
import os
import time
import asyncio


load_dotenv()

TELEGRAM_USERNAME_ADMIN = os.getenv('TELEGRAM_USERNAME_ADMIN')
MAIL_ADMIN = os.getenv('MAIL_ADMIN')


router = Router()


# ============================================================
# MACHINE STATE (FSM) - для ввода моделей
# ============================================================

class ParserStates(StatesGroup):
    waiting_for_models = State() # Ожидаем ввод моделей


# ============================================================
# ФУНКЦИЯ ПАРСИНГА
# ============================================================

async def parsing(message: Message, models_list: list) -> bool:
    """
    Асинхронная функция парсинга с отправкой статусов в бот
    """
    if not models_list:
        await message.answer("❌ Список моделей пуст!")
        return False

    # ----- Парсим все модели -----
    results = []          # Список успешно спарсенных моделей
    successful = 0        # Счетчик успешных парсингов
    failed = 0            # Счетчик ошибок
    
    # Общее время выполнения
    start_time = time.time()

    total_models = len(models_list)
    
    # Создаем сообщение для прогресса
    progress_msg = await message.answer("🔄 Запуск парсинга...")
    
    # Отправляем список моделей (разбиваем по частям, если длинный)
    if total_models > 10:
        models_list = ", ".join(models_list[:10]) + f"... и еще {total_models - 10}"
    else:
        models_list = ", ".join(models_list)
    await message.answer(f"📋 Модели для парсинга:\n{models_list}")

    
    for idx, model_name in enumerate(models_list, 1):
        try:
            # Парсим текущую модель
            product = parse_by_search(model_name)
            logger.info(f"[{idx}/{len(models_list)}] Парсинг: {model_name}")
                
            # Проверяем, удалось ли спарсить
            if product.brand and product.model:
                results.append(product)
                successful += 1
                logger.info(f"✅ Успешно: {product.brand} {product.model}")
                
                status = "✅ УСПЕШНО"
            else:
                failed += 1
                logger.warning(f"❌ Не удалось спарсить: {model_name}")
                    
                status = "❌ НЕ УДАЛОСЬ"

            # Обновляем сообщение с прогрессом
            progress_text = (
                f"🔄 **Парсинг** [{idx}/{total_models}]\n"
                f"📌 {model_name}\n"
                f"📊 Статус: {status}\n"
                f"✅ Успешно: {successful} | ❌ Ошибок: {failed}\n"
                f"📈 Прогресс: {idx/total_models*100:.1f}%"
            )
            
            try:
                await progress_msg.edit_text(progress_text)
            except Exception:
                # Если не можем отредактировать, отправляем новое сообщение
                await message.answer(progress_text)
                progress_msg = await message.answer("📊 Продолжаем...")
            
            # Пауза между запросами (чтобы не нагружать сайт)
            if idx < total_models:
                await asyncio.sleep(DELAYS.get('between_requests'))

        except Exception as e:
            # Ловим любые ошибки
            failed += 1
            logger.error(f"❌ Ошибка: {model_name}")
            logger.debug(f"Детали: {e}")

            # Обновляем с ошибкой
            await progress_msg.edit_text(
                f"⚠️ **Ошибка** [{idx}/{total_models}]\n"
                f"📌 {model_name}\n"
                f"❌ {str(e)[:50]}\n"
                f"✅ Успешно: {successful} | ❌ Ошибок: {failed}"
            )

    # Вычисляем время выполнения
    elapsed_time = time.time() - start_time

    await progress_msg.edit_text(
        f"🎉 **ПАРСИНГ ЗАВЕРШЕН!**\n\n"
        f"✅ Успешно: {successful}\n"
        f"❌ Ошибок: {failed}\n"
        f"⏱️ Время: {elapsed_time:.2f} сек\n"
        f"📈 Успешность: {successful/total_models*100:.1f}%"
    )

    # ----- Сохраняем результаты -----
    if results:
        # Сохраняем в JSON
        save_results(results)
        # Сохраняем в CSV
        save_as_csv(results)
        # Выводим сводку
        print_summary(results)
        logger.info("🎉 ПАРСИНГ ЗАВЕРШЕН")

        await message.answer(
            f"💾 Результаты сохранены:\n"
            f"📄 JSON отправляю...\n"
            f"📊 CSV: отправляю...\n"
            f"📦 Всего записей: {len(results)}"
        )

        # ----- ОТПРАВЛЯЕМ ФАЙЛЫ -----
        await send_result_files(message)

        return True
    else:
        logger.error("❌ Не удалось спарсить ни одной модели")
        await message.answer("❌ Не удалось спарсить ни одной модели")
        return False


async def send_result_files(message: Message) -> None:
    """
    Отправляет файлы results.json и results.csv в чат
    """
    json_path = OUTPUT.get('json_filename')
    csv_path = OUTPUT.get('csv_filename')

    files_sent = 0

    # Отправка JSON
    if os.path.exists(json_path):
        try:
            json_file = FSInputFile(json_path)
            await message.answer_document(
                document=json_file,
                caption=f"📄 Результаты в JSON\n📦 {os.path.getsize(json_path) / 1024:.1f} KB"
            )
            files_sent += 1
            logger.info(f"📤 Отправлен JSON файл")
        except Exception as e:    
            logger.error(f"❌ Ошибка отправки JSON: {e}")
            await message.answer(f"❌ Не удалось отправить JSON: {e}")
    else:
        await message.answer(f"⚠️ Файл {json_path} не найден")

    # Отправка CSV
    if os.path.exists(csv_path):
        try:
            csv_file = FSInputFile(csv_path)
            await message.answer_document(
                document=csv_file,
                caption=f"📊 Результаты в CSV\n📦 {os.path.getsize(csv_path) / 1024:.1f} KB"
            )
            files_sent += 1
            logger.info(f"📤 Отправлен CSV файл")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки CSV: {e}")
            await message.answer(f"❌ Не удалось отправить CSV: {e}")
    else:
        await message.answer(f"⚠️ Файл {csv_path} не найден")
    
    if files_sent == 2:
        await message.answer("✅ Все файлы успешно отправлены!")
    elif files_sent == 1:
        await message.answer("⚠️ Отправлен только один файл")
    else:
        await message.answer("❌ Не удалось отправить файлы")


# ============================================================
# ФУНКЦИЯ ДЛЯ РАЗБОРА МОДЕЛЕЙ ИЗ ТЕКСТА
# ============================================================


def parse_models_from_text(text: str) -> list:
    """
    Разбирает текст на список моделей.
    Поддерживает:
    - Каждая модель на новой строке
    - Модели через запятую
    - Модели через точку с запятой
    - Модели через пробел (если не содержат пробелов внутри)
    """
    # Сначала пробуем разбить по строкам
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

    models = []
    
    # Обрабатываем каждую строку
    for line in lines:
        # Пробуем разбить по запятым
        if ',' in line:
            parts = [p.strip() for p in line.split(',') if p.strip()]
            models.extend(parts)
        # Или по точке с запятой
        elif ';' in line:
            parts = [p.strip() for p in line.split(';') if p.strip()]
            models.extend(parts)
        # Если это одна модель
        else:
            models.append(line)
    
    # Удаляем дубликаты и пустые строки
    models = list(dict.fromkeys([m for m in models if m]))
    
    return models
    

# ============================================================
# ХЕНДЛЕРЫ
# ============================================================

@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        'Добро пожаловать в парсинг Citilink! 🛒\n\n'
        '📌 **Как использовать:**\n'
        '1️⃣ Нажмите "Ввести модели" или /set_models\n'
        '2️⃣ Введите список моделей\n'
        '3️⃣ Нажмите "Начать парсинг" или /parse\n\n'
        '📌 **Форматы ввода:**\n'
        '• Каждая модель на новой строке\n'
        '• Через запятую: модель1, модель2\n'
        '• Через точку с запятой: модель1; модель2',
        reply_markup=kb.main
    )

@router.message(Command('help'))
async def cmd_help(message: Message) -> None:
    await message.answer(
        '🤖 **Помощь по боту:**\n\n'
        '📌 /start - Главное меню\n'
        '📌 /help - Эта справка\n'
        '📌 /set_models - Ввести модели\n'
        '📌 /parse - Запустить парсинг\n'
        '📌 /get_files - Получить последние результаты\n\n'
        '📌 "Ввести модели" - Ввод моделей\n'
        '📌 "Начать парсинг" - Запуск парсинга'
    )

@router.message(Command('set_models'))
async def set_models_command(message: Message, state: FSMContext) -> None:
    """Команда для ввода моделей"""
    await state.set_state(ParserStates.waiting_for_models)
    await message.answer(
        '📝 **Введите модели для парсинга**\n\n'
        'Поддерживаемые форматы:\n'
        '• Каждая модель на новой строке\n'
        '• Через запятую: модель1, модель2\n'
        '• Через точку с запятой: модель1; модель2\n\n'
        'Пример:\n'
        'Gorenje ECT643SYB\n'
        'Gorenje ECT641BCSC\n'
        'Candy CHXC64TDB\n\n'
        'Или: Gorenje ECT643SYB, Gorenje ECT641BCSC, Candy CHXC64TDB\n\n'
        '✏️ Введите модели:'
    )

@router.message(ParserStates.waiting_for_models)
async def process_models_input(message: Message, state: FSMContext) -> None:
    """Обработка введенных моделей"""
    models = parse_models_from_text(message.text)

    if not models:
        await message.answer("❌ Не удалось распознать модели. Попробуйте еще раз.")
        return
    
    # Сохраняем модели в состояние
    await state.update_data(models=models)

    # Просто выходим из состояния, но данные сохраняем
    await state.set_state(None)

    # Показываем найденные модели
    models_text = "\n".join([f"• {m}" for m in models[:10]])
    if len(models) > 10:
        models_text += f"\n... и еще {len(models) - 10} моделей"

    await message.answer(
        f"✅ **Найдено {len(models)} моделей:**\n\n{models_text}\n\n"
        f"📌 Нажмите 'Начать парсинг' или введите /parse для запуска"
    )

@router.message(Command('parse'))
async def parse_command(message: Message, state: FSMContext) -> None:
    """Запуск парсинга по сохраненным моделям"""
    data = await state.get_data()
    models = data.get('models', [])
    
    if not models:
        await message.answer(
            "❌ Список моделей пуст!\n"
            "Сначала введите модели через /set_models"
        )
        return
    
    await message.answer(f"🔄 Запускаю парсинг {len(models)} моделей...")
    
    try:
        success = await parsing(message, models)
        if success:
            await message.answer("✅ Парсинг успешно завершен!")
        else:
            await message.answer("❌ Парсинг завершен с ошибками.")
    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        await message.answer(f"❌ Произошла ошибка: {str(e)}")


@router.message(F.text == 'Ввести модели')
async def set_models_button(message: Message, state: FSMContext) -> None:
    """Кнопка для ввода моделей"""
    await set_models_command(message, state)


@router.message(F.text == 'Начать парсинг')
async def parse_button(message: Message, state: FSMContext) -> None:
    """Кнопка для запуска парсинга"""
    await parse_command(message, state)

@router.message(F.text == 'О нас')
async def about_us(message: Message) -> None:
    await message.answer(
        '🔍 Парсер сайта Citilink.com\n'
        'Бот собирает информацию о товарах\n'
        'и сохраняет результаты в JSON и CSV форматах'
    )

@router.message(F.text == 'Контакты')
async def contacts(message: Message) -> None:
    await message.answer(
        f'📱 Telegram: @{TELEGRAM_USERNAME_ADMIN}\n'
        f'📧 Почта: {MAIL_ADMIN}'
    )

@router.message(Command('get_files'))
async def get_files_command(message: Message) -> None:
    """Отправка последних результатов"""
    await send_result_files(message)

@router.message(F.text)
async def handle_other(message: Message) -> None:
    await message.answer(
        '🤔 Я не понял твое сообщение.\n'
        'Используй кнопки меню или команду /help'
    )