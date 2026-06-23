# ============================================================
# ТЕСТОВЫЙ ПАРСИНГ РАЗНЫХ ТОВАРОВ
# ============================================================

import sys
from pathlib import Path

# Добавляем корневую папку в PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.parser import parse_cooktop_by_search
from src.utils import save_results, save_as_csv
from src.logger import logger
import json
import time


def test_multiple_models():
    """
    Тестирует парсинг разных товаров (не только варочных панелей).
    Добавь сюда любые модели для проверки.
    """
    
    # ----- СПИСОК ТОВАРОВ ДЛЯ ТЕСТА -----
    # Добавь сюда любые товары с Citilink
    test_models = [
        # Варочные панели (уже работают)
        "Gorenje ECT643SYB",
        "Candy CHXC64TDB",
        
        # Другие категории товаров
        "Холодильник Samsung RB33J3000SA",      # Холодильник
        "Стиральная машина LG F2J5HS0W",        # Стиралка
        "Телевизор Xiaomi Mi TV 5S 55",         # Телевизор
        "Пылесос Dyson V15 Detect Absolute",    # Пылесос
        "Микроволновая печь Samsung GE83KRS",   # Микроволновка
        "Посудомоечная машина Bosch SMS6ZCW10R", # Посудомойка
        "Умная колонка Яндекс Станция Мини",    # Колонка
        "Ноутбук ASUS TUF Gaming F15",          # Ноутбук
        "Наушники Sony WH-1000XM5",             # Наушники
    ]
    
    logger.info("=" * 60)
    logger.info(f"🧪 ТЕСТОВЫЙ ПАРСИНГ РАЗНЫХ ТОВАРОВ")
    logger.info("=" * 60)
    logger.info(f"📦 Товаров для теста: {len(test_models)}")
    
    results = []
    successful = 0
    failed = 0
    
    start_time = time.time()
    
    for idx, model_name in enumerate(test_models, 1):
        print("\n" + "=" * 60)
        print(f"[{idx}/{len(test_models)}] Тестируем: {model_name}")
        print("=" * 60)
        
        try:
            # Парсим товар
            result = parse_cooktop_by_search(model_name)
            
            # Проверяем результат
            if result.brand and result.model:
                results.append(result)
                successful += 1
                
                # Выводим информацию о товаре
                data = result.model_dump(by_alias=True)
                filled_count = sum(1 for v in data.values() if v)
                
                print(f"\n✅ УСПЕШНО!")
                print(f"  Бренд: {result.brand}")
                print(f"  Модель: {result.model}")
                print(f"  Цена: {result.price or 'Не найдена'}")
                print(f"  Характеристик: {len(result.characteristics)}")
                print(f"  Всего полей: {len(data)}")
                print(f"  Заполнено: {filled_count}")
                
                # Проверяем наличие картинки
                if result.image_url:
                    print(f"  🖼️ Картинка есть")
                else:
                    print(f"  ⚠️ Картинка не найдена")
                    
            else:
                failed += 1
                print(f"\n❌ НЕ УДАЛОСЬ спарсить: {model_name}")
                
        except Exception as e:
            failed += 1
            print(f"\n❌ ОШИБКА при парсинге: {model_name}")
            print(f"  Детали: {e}")
        
        # Пауза между запросами
        if idx < len(test_models):
            print(f"\n⏳ Пауза 2 секунды...")
            time.sleep(2)
    
    # Статистика
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("📊 СТАТИСТИКА ТЕСТА:")
    print("=" * 60)
    print(f"  ✅ Успешно: {successful}/{len(test_models)}")
    print(f"  ❌ Ошибок: {failed}")
    print(f"  ⏱️ Время: {elapsed_time:.2f} сек")
    
    # Сохраняем результаты
    if results:
        save_results(results, "test_results.json")
        save_as_csv(results, "test_results.csv")
        print("\n✅ Результаты сохранены в:")
        print("  - test_results.json")
        print("  - test_results.csv")
    else:
        print("\n❌ Не удалось спарсить ни одного товара")


def test_single_model():
    """Быстрый тест одной модели."""
    model_name = "Холодильник Samsung RB33J3000SA"
    
    logger.info("=" * 60)
    logger.info(f"🧪 БЫСТРЫЙ ТЕСТ: {model_name}")
    logger.info("=" * 60)
    
    result = parse_cooktop_by_search(model_name)
    
    if result.brand and result.model:
        print(f"\n✅ УСПЕШНО!")
        print(f"  Бренд: {result.brand}")
        print(f"  Модель: {result.model}")
        print(f"  Цена: {result.price or 'Не найдена'}")
        print(f"  Характеристик: {len(result.characteristics)}")
        
        # Сохраняем результат
        data = result.model_dump(by_alias=True)
        with open('test_single_result.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("\n✅ Результат сохранён в test_single_result.json")
    else:
        print(f"\n❌ НЕ УДАЛОСЬ спарсить: {model_name}")


if __name__ == "__main__":
    # Выбери, что запускать:
    
    # 1. Тест нескольких товаров (рекомендуется)
    test_multiple_models()
    
    # 2. Или быстрый тест одного товара
    # test_single_model()