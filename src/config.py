# ============================================================
# ЕДИНЫЙ КОНФИГУРАЦИОННЫЙ ФАЙЛ
# Все настройки проекта в одном месте
# ============================================================


# ============================================================
#    НАСТРОЙКИ САЙТА
# ============================================================

# Базовый URL для поиска (в {query} подставляется название модели)
SEARCH_URL = "https://www.citilink.ru/search/?text={query}"

# CSS-классы для парсинга характеристик (найдены вручную на сайте)
SELECTORS = {
    # Класс для заголовка характеристики
    'property_title': 'es7ht5z5 e1a7a4n70 app-catalog-ztw6b0-StyledTypography--getTypographyStyle-composeBreakpointsStyles--arrayOfStylesByBreakpoints-StyledText--getTextStyle-Text--StyledTextComponent-components--PropertiesItemTitle-components--propertiesItemTitleStyles e1d9wgme0',
    
    # Класс для значения характеристики
    'property_value': 'es7ht5z6 e1a7a4n70 app-catalog-1phzsx4-StyledTypography--getTypographyStyle-composeBreakpointsStyles--arrayOfStylesByBreakpoints-StyledText--getTextStyle-Text--StyledTextComponent-components--PropertiesValue-components--propertiesValueStyles e1d9wgme0',

    # Класс для контейнера со списком характеристик
    'properties_container': 'app-catalog-li9fsz-components--Properties components--propertiesStyles es7ht5z0',
    
    # Класс для элемента характеристики (обёртка заголовка + значения)
    'property_item': 'app-catalog-7g4f64-Flex--StyledFlex-components--PropertiesItem-components--propertiesItemStyles es7ht5z1',
    
    # Класс для контейнера заголовка характеристики
    'title_container': 'app-catalog-61b1vd-Flex--StyledFlex-components--PropertiesNameWrapper-components--propertiesNameWrapperStyles es7ht5z2',
}

# Класс для парсинга цены (основной идентификатор)
PRICE_SELECTOR = 'e4ahr150'

# Класс контейнера с изображениями на странице товара
IMAGE_CONTAINER_SELECTOR = 'e9atu2e0'


# ============================================================
#    НАСТРОЙКИ SELENIUM (управление браузером)
# ============================================================

SELENIUM_SETTINGS = {
    'headless': True,  # True = браузер невидим (быстрее), False = виден (для отладки)
    'window_size': '1920,1080',  # Размер окна браузера
    'implicitly_wait': 10,  # Максимальное время ожидания элементов (сек)
    'page_load_timeout': 60,  # Таймаут загрузки страницы (сек)
}

# User-Agent для браузера (имитируем реальный браузер)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


# ============================================================
#    ЗАДЕРЖКИ И ТАЙМАУТЫ (оптимизация скорости)
# ============================================================

DELAYS = {
    'between_requests': 1.0, # Пауза между запросами к разным моделям (сек)
    'after_click': 1.5, # Пауза после клика по ссылке (сек)
    'after_search': 1.5, # Пауза после загрузки результатов поиска (сек)
    'after_properties': 1.0,  # Пауза после загрузки страницы характеристик (сек)
    'after_scroll': 0.3,  # Пауза после скролла (сек)
}

# Таймауты для WebDriverWait (ожидание элементов на странице)
WAIT_TIMEOUTS = {
    'product_link': 15,  # Ожидание ссылки на товар (сек)
    'page_load': 20,  # Ожидание загрузки страницы (сек)
}


# ============================================================
#    НАСТРОЙКИ ЛОГИРОВАНИЯ
# ============================================================

LOGGING = {
    'enabled': True,            # Включить логирование
    'log_dir': 'logs',          # Папка для хранения логов
    'name': 'CitilinkParser',   # Имя логгера (используется в названии файлов)
    'console_level': 'INFO',    # Уровень для консоли (DEBUG, INFO, WARNING, ERROR)
    'file_level': 'DEBUG',      # Уровень для файла (записываем всё)
    'date_format': '%H:%M:%S',  # Формат времени в логах
    'log_format': '[%(asctime)s] [%(levelname)s] %(message)s',  # Формат сообщения
}


# ============================================================
#    НАСТРОЙКИ СОХРАНЕНИЯ РЕЗУЛЬТАТОВ
# ============================================================

OUTPUT = {
    'json_filename': 'output/results.json',  # Имя файла для JSON
    'csv_filename': 'output/results.csv',    # Имя файла для CSV
    'json_indent': 4,           # Отступы в JSON (для читаемости)
    'csv_delimiter': ';',       # Разделитель в CSV (точка с запятой для Excel)
    'encoding': 'utf-8-sig',    # Кодировка для CSV (с BOM для Excel)
}


# ============================================================
#    СПИСОК МОДЕЛЕЙ ДЛЯ ПАРСИНГА
# ============================================================

# Модели для парсинга (названия должны точно совпадать с поиском на сайте)
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