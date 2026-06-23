# ============================================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# Логи выводятся одновременно в консоль и в файл
# ============================================================

import logging
import sys
from pathlib import Path
from datetime import datetime
from src.config import LOGGING


def setup_logger() -> logging.Logger:
    """
    Настраивает и возвращает логгер.
    
    Особенности:
    - Логи пишутся в консоль (уровень INFO) и в файл (уровень DEBUG)
    - Ошибки дублируются в отдельный файл
    - Создаётся новая папка logs/ если её нет
    - Имя файла лога содержит дату
    """
    # Проверяем, включено ли логирование в конфиге
    if not LOGGING.get('enabled', True):
        # Если выключено - создаём "пустой" логгер (ничего не делает)
        logger = logging.getLogger(LOGGING.get('name', 'CitilinkParser'))
        logger.addHandler(logging.NullHandler())
        return logger
    
    # Получаем имя логгера из конфига
    name = LOGGING.get('name', 'CitilinkParser')
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Самый низкий уровень - записываем всё
    
    # Если логгер уже настроен - не дублируем handlers
    if logger.handlers:
        return logger
    
    # --- СОЗДАЁМ ПАПКУ ДЛЯ ЛОГОВ ---
    log_path = Path(LOGGING.get('log_dir', 'logs'))
    log_path.mkdir(parents=True, exist_ok=True)  # exist_ok=True - не выдаём ошибку, если папка есть
    
    # --- ФОРМАТ ЛОГОВ ---
    # Берём настройки из конфига или используем значения по умолчанию
    log_format = LOGGING.get('log_format', '[%(asctime)s] [%(levelname)s] %(message)s')
    date_format = LOGGING.get('date_format', '%H:%M:%S')
    formatter = logging.Formatter(log_format, date_format)
    
    # --- ХКОНСОЛЬ (видим процесс в реальном времени) ---
    console_level = getattr(logging, LOGGING.get('console_level', 'INFO'))
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)  # Например, INFO - видим только важное
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # --- ФАЙЛ (все логи для анализа) ---
    # Имя файла: CitilinkParser_2026-06-23.log
    timestamp = datetime.now().strftime("%Y-%m-%d")
    log_file = log_path / f"{name}_{timestamp}.log"
    
    file_level = getattr(logging, LOGGING.get('file_level', 'DEBUG'))
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)  # DEBUG - записываем всё
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # --- ОТДЕЛЬНЫЙ ФАЙЛ ДЛЯ ОШИБОК (удобно искать проблемы) ---
    error_file = log_path / f"{name}_errors_{timestamp}.log"
    error_handler = logging.FileHandler(error_file, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)  # Только ERROR и выше
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


# Создаём глобальный логгер (доступен из любого файла через import)
logger = setup_logger()