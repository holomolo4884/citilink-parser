# ============================================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================================

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "CitilinkParser", log_dir: str = "logs") -> logging.Logger:
    """
    Настраивает и возвращает логгер.
    
    Аргументы:
        name: Имя логгера
        log_dir: Папка для хранения логов
    
    Возвращает:
        logging.Logger: Настроенный логгер
    """
    # Создаём папку для логов
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Имя файла лога с датой
    timestamp = datetime.now().strftime("%Y-%m-%d")
    log_file = log_path / f"{name}_{timestamp}.log"
    
    # Создаём логгер
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Уровень DEBUG - всё записываем
    
    # Формат логов
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ----- Handler для файла (все уровни) -----
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # ----- Handler для консоли (только INFO и выше) -----
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # ----- Handler для ошибок (отдельный файл) -----
    error_file = log_path / f"{name}_errors_{timestamp}.log"
    error_handler = logging.FileHandler(error_file, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


# Создаём глобальный логгер
logger = setup_logger()