# src/utils.py
# ============================================================
# УТИЛИТЫ ДЛЯ СОХРАНЕНИЯ ДАННЫХ
# Сохранение в JSON и CSV с прогресс-баром
# ============================================================

import json
import csv
from pathlib import Path
from typing import List
from src.models import CooktopProperties
from src.logger import logger
from tqdm import tqdm  # Прогресс-бар


# ============================================================
# СОХРАНЕНИЕ В JSON
# ============================================================
def save_results(data: List[CooktopProperties], filename: str = "output/results.json"):
    """
    Сохраняет данные в JSON файл.
    
    Аргументы:
        data: Список объектов CooktopProperties
        filename: Путь к файлу (по умолчанию: output/results.json)
    """
    logger.info(f"Сохранение результатов в JSON: {filename}")

    # Создаем папку output/, если её нет
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Подготавливаем данные для сохранения
    result_data = []
    
    # Проходим по всем моделям с прогресс-баром
    for item in tqdm(data, desc="  📝 Подготовка JSON"):
        # Создаем словарь с базовыми полями
        item_dict = {
            "Бренд": item.brand,
            "Модель": item.model,
            "Цена": item.price,
            "Ссылка на изображение": item.image_url,
        }
        # Добавляем все динамические характеристики
        item_dict.update(item.characteristics)
        result_data.append(item_dict)
    
    # Сохраняем в JSON с отступами для читаемости
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"JSON сохранён: {len(result_data)} записей")


# ============================================================
# СОХРАНЕНИЕ В CSV
# ============================================================
def save_as_csv(data: List[CooktopProperties], filename: str = "output/results.csv"):
    """
    Сохраняет данные в CSV файл с разделителем ; (для Excel).
    
    Аргументы:
        data: Список объектов CooktopProperties
        filename: Путь к файлу (по умолчанию: output/results.csv)
    """
    # Проверяем, есть ли данные
    if not data:
        logger.warning("Нет данных для сохранения в CSV")
        return
    
    logger.info(f"Сохранение результатов в CSV: {filename}")
    
    # Создаем папку output/, если её нет
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # ----- ШАГ 1: Собираем все данные и все возможные поля -----
    all_rows = []          # Список словарей с данными
    all_fieldnames = set() # Множество всех названий полей
    
    for item in tqdm(data, desc="  📝 Подготовка CSV"):
        # Базовые поля
        row = {
            "Бренд": item.brand or "",
            "Модель": item.model or "",
            "Цена": item.price or "",
            "Ссылка на изображение": item.image_url or "",
        }
        # Добавляем характеристики
        row.update(item.characteristics)
        
        all_rows.append(row)
        all_fieldnames.update(row.keys())
    
    # ----- ШАГ 2: Сортируем поля -----
    # Базовые поля идут первыми (в фиксированном порядке)
    base_fields = ["Бренд", "Модель", "Цена", "Ссылка на изображение"]
    
    # Остальные поля сортируем по алфавиту
    other_fields = sorted([f for f in all_fieldnames if f not in base_fields])
    
    # Итоговый список полей
    fieldnames = base_fields + other_fields
    
    # ----- ШАГ 3: Записываем CSV -----
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        # Создаем writer с разделителем ; (точка с запятой)
        # Все поля в кавычках (quoting=csv.QUOTE_ALL)
        writer = csv.DictWriter(
            f, 
            fieldnames=fieldnames,
            delimiter=';',
            quoting=csv.QUOTE_ALL
        )
        
        # Записываем заголовки
        writer.writeheader()
        
        # Записываем данные
        for row in tqdm(all_rows, desc="  📝 Запись CSV"):
            # Очищаем значения от переносов строк (чтобы не сломать CSV)
            clean_row = {}
            for key, value in row.items():
                if isinstance(value, str):
                    clean_row[key] = value.replace('\n', ' ').replace('\r', ' ')
                else:
                    clean_row[key] = value
            writer.writerow(clean_row)
    
    logger.info(f"CSV сохранён: {len(all_rows)} записей, {len(fieldnames)} полей")


# ============================================================
# ВЫВОД СВОДКИ
# ============================================================
def print_summary(data: List[CooktopProperties]):
    """
    Выводит краткую сводку по спарсенным данным.
    
    Аргументы:
        data: Список объектов CooktopProperties
    """
    if not data:
        logger.warning("Нет данных для сводки")
        return
    
    logger.info("Вывод сводки по данным")
    
    print("\n" + "=" * 60)
    print("📊 СВОДКА ПО СПАРСЕННЫМ ДАННЫМ:")
    print("=" * 60)
    
    # Проходим по всем моделям и выводим основную информацию
    for i, item in enumerate(data, 1):
        brand = item.brand or "Не указан"
        model = item.model or "Не указана"
        price = item.price or "Цена не найдена"
        count = len(item.characteristics)  # Количество характеристик
        print(f"{i}. {brand} {model} — {price} ({count} хар-к)")