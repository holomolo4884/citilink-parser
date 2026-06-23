# test/test_parser.py
# ============================================================
# ТЕСТОВЫЙ ПАРСИНГ ОДНОЙ МОДЕЛИ
# ============================================================

import sys
import os
from pathlib import Path

# Добавляем корневую папку в PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.parser import parse_cooktop_by_search
from src.utils import save_results, save_as_csv, print_summary
from src.logger import logger
import json
import time


def test_single_model():
    """Тестирует парсинг одной модели."""
    model_name = "Gorenje ECT643SYB"
    
    logger.info("=" * 60)
    logger.info(f"ТЕСТОВЫЙ ПАРСИНГ: {model_name}")
    logger.info("=" * 60)
    
    print("=" * 60)
    print(f"🧪 ТЕСТОВЫЙ ПАРСИНГ: {model_name}")
    print("=" * 60)
    
    start_time = time.time()
    
    result = parse_cooktop_by_search(model_name)
    
    elapsed_time = time.time() - start_time
    logger.info(f"Время выполнения: {elapsed_time:.2f} сек")
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТ ТЕСТА:")
    print("=" * 60)
    
    data = result.model_dump(by_alias=True)
    
    filled_count = 0
    print("\n📋 СОБРАННЫЕ ДАННЫЕ:")
    print("-" * 40)
    
    for key, value in sorted(data.items()):
        if value:
            filled_count += 1
            if len(str(value)) > 80:
                display_value = str(value)[:80] + "..."
            else:
                display_value = value
            print(f"  {key}: {display_value}")
            logger.debug(f"{key}: {value}")
    
    print("-" * 40)
    print(f"📊 Всего полей: {len(data)}")
    print(f"📊 Заполнено: {filled_count}")
    print(f"📊 Пустых: {len(data) - filled_count}")
    print(f"⏱️ Время: {elapsed_time:.2f} сек")
    
    logger.info(f"Результат: {filled_count}/{len(data)} полей заполнено")
    
    # Сохраняем результат
    with open('test_result.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("\n✅ Полный результат сохранен в test_result.json")
    logger.info("Результат сохранён в test_result.json")
    
    if result.brand and result.model:
        save_results([result], "test_result.json")
        save_as_csv([result], "test_result.csv")
        print("✅ CSV сохранен в test_result.csv")
        logger.info("CSV сохранён в test_result.csv")
    
    print("\n" + "=" * 60)
    print("✅ ТЕСТ ЗАВЕРШЕН")
    print("=" * 60)
    logger.info("Тест завершен")


if __name__ == "__main__":
    test_single_model()