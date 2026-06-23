# test/test_parser.py
# ============================================================
# ТЕСТОВЫЙ ПАРСИНГ ОДНОЙ МОДЕЛИ
# Используется для отладки и проверки работы парсера
# ============================================================

import sys
from pathlib import Path

# Добавляем корневую папку в PYTHONPATH (чтобы найти src/)
# Path(__file__).parent.parent -> поднимаемся на два уровня вверх от test/
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.parser import parse_cooktop_by_search
from src.utils import save_results, save_as_csv
from src.logger import logger
from src.config import MODELS_TO_PARSE
import json
import time


def test_single_model():
    """Тестирует парсинг одной модели (первой из списка)."""
    
    # Берём первую модель из списка в конфиге
    model_name = MODELS_TO_PARSE[0]
    
    logger.info("=" * 60)
    logger.info(f"🧪 ТЕСТОВЫЙ ПАРСИНГ: {model_name}")
    logger.info("=" * 60)
    
    # Засекаем время выполнения
    start_time = time.time()
    
    # Парсим модель
    result = parse_cooktop_by_search(model_name)
    
    elapsed_time = time.time() - start_time
    
    # Получаем данные с русскими ключами
    data = result.model_dump(by_alias=True)
    
    # ----- Выводим результат -----
    filled_count = 0
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТ ТЕСТА:")
    print("=" * 60)
    print("\n📋 СОБРАННЫЕ ДАННЫЕ:")
    print("-" * 40)
    
    # Выводим все непустые поля
    for key, value in sorted(data.items()):
        if value:
            filled_count += 1
            # Обрезаем длинные значения для читаемости
            if len(str(value)) > 80:
                display_value = str(value)[:80] + "..."
            else:
                display_value = value
            print(f"  {key}: {display_value}")
    
    # ----- Выводим статистику -----
    print("-" * 40)
    print(f"📊 Всего полей: {len(data)}")
    print(f"📊 Заполнено: {filled_count}")
    print(f"📊 Пустых: {len(data) - filled_count}")
    print(f"⏱️ Время: {elapsed_time:.2f} сек")
    
    # ----- Сохраняем результат -----
    # JSON
    with open('test_result.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("\n✅ Результат сохранён в test_result.json")
    
    # CSV (если данные есть)
    if result.brand and result.model:
        save_results([result], "test_result.json")
        save_as_csv([result], "test_result.csv")
        print("✅ CSV сохранён в test_result.csv")
    
    logger.info("✅ ТЕСТ ЗАВЕРШЕН")


if __name__ == "__main__":
    test_single_model()