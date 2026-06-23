# main.py
# ============================================================
# ТОЧКА ВХОДА В ПРОГРАММУ
# Запускает парсинг всех моделей из списка
# ============================================================

from src.parser import parse_cooktop_by_search
from src.utils import save_results, save_as_csv, print_summary
from src.logger import logger
from tqdm import tqdm  # Прогресс-бар
import time
import sys

# ============================================================
# СПИСОК МОДЕЛЕЙ ДЛЯ ПАРСИНГА
# ============================================================
# Добавляй сюда любые модели, которые нужно спарсить
# Названия должны точно соответствовать тому, как они ищутся на сайте
MODELS_TO_PARSE = [
    "Gorenje ECT643SYB",
    "Gorenje ECT641BCSC",
    "Candy CHXC64TDB",
    "Kuppersberg ECO 603",
    "Kuppersberg 400",
    "Kuppersberg ECS 635",
    "Midea MCH-B632C",
    "Kuppersberg ECS 624",
    "Midea MCH-B641C",
    "Weissgauff HV 633 BS"
]


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================
def main():
    """Главная функция: запускает парсинг и сохраняет результаты."""
    logger.info("=" * 60)
    logger.info("ЗАПУСК ПАРСЕРА")
    logger.info("=" * 60)
    logger.info(f"Моделей для парсинга: {len(MODELS_TO_PARSE)}")
    
    # ----- Парсим все модели -----
    results = []          # Список успешно спарсенных моделей
    successful = 0        # Счетчик успешных парсингов
    failed = 0            # Счетчик ошибок
    
    # Общее время выполнения
    start_time = time.time()

    # Прогресс-бар для визуального контроля
    with tqdm(total=len(MODELS_TO_PARSE), desc="📊 Парсинг", unit="модель") as pbar:
        
        for idx, model_name in enumerate(MODELS_TO_PARSE, 1):
            # Обновляем описание прогресс-бара (показываем текущую модель)
            pbar.set_description(f"📊 {model_name[:20]}")
            
            try:
                # Парсим текущую модель
                cooktop = parse_cooktop_by_search(model_name)
                logger.info(f"[{idx}/{len(MODELS_TO_PARSE)}] Парсинг: {model_name}")
                
                # Проверяем, удалось ли спарсить
                if cooktop.brand and cooktop.model:
                    results.append(cooktop)
                    successful += 1
                    logger.info(f"✅ Успешно: {cooktop.brand} {cooktop.model}")
                    # Обновляем прогресс-бар с дополнительной информацией
                    pbar.set_postfix({
                        'успешно': successful,
                        'ошибок': failed
                    })
                else:
                    failed += 1
                    logger.warning(f"❌ Не удалось спарсить: {model_name}")
                    
            except Exception as e:
                # Ловим любые ошибки
                failed += 1
                logger.error(f"Ошибка при парсинге {model_name}")
                logger.debug(f"Детали: {e}")
            
            # Обновляем прогресс-бар (одна модель обработана)
            pbar.update(1)
            
            # Пауза между запросами (чтобы не нагружать сайт)
            if idx < len(MODELS_TO_PARSE):
                time.sleep(1)
    
    # Вычисляем время выполнения
    elapsed_time = time.time() - start_time

    # ----- Выводим статистику -----
    logger.info("=" * 60)
    logger.info("📊 СТАТИСТИКА:")
    logger.info(f"  ✅ Успешно: {successful}")
    logger.info(f"  ❌ Ошибок: {failed}")
    logger.info(f"  ⏱️ Время: {elapsed_time:.2f} сек")

    # ----- Сохраняем результаты -----
    if results:
        # Сохраняем в JSON
        save_results(results)
        # Сохраняем в CSV
        save_as_csv(results)
        # Выводим сводку
        print_summary(results)
        logger.info("Парсинг завершен успешно")
    else:
        logger.error("Не удалось спарсить ни одной модели")


# ============================================================
# ЗАПУСК ПРОГРАММЫ
# ============================================================
if __name__ == "__main__":
    main()