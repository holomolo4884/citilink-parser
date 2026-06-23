# ============================================================
# КОНФИГУРАЦИЯ ПАРСЕРА
# Здесь хранятся все настройки: URL, селекторы, задержки
# ============================================================

# Базовые URL для работы с сайтом
BASE_URL = "https://www.citilink.ru"  # Главный домен
SEARCH_URL = "https://www.citilink.ru/search/?text={query}"  # Шаблон поиска

# Заголовки запроса (имитируем реальный браузер)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# CSS-классы для парсинга характеристик (найдены вручную на сайте)
SELECTORS = {
    # Класс для заголовка характеристики (например: "Бренд")
    'property_title': 'es7ht5z5 e1a7a4n70 app-catalog-ztw6b0-StyledTypography--getTypographyStyle-composeBreakpointsStyles--arrayOfStylesByBreakpoints-StyledText--getTextStyle-Text--StyledTextComponent-components--PropertiesItemTitle-components--propertiesItemTitleStyles e1d9wgme0',
    
    # Класс для значения характеристики (например: "GORENJE")
    'property_value': 'es7ht5z6 e1a7a4n70 app-catalog-1phzsx4-StyledTypography--getTypographyStyle-composeBreakpointsStyles--arrayOfStylesByBreakpoints-StyledText--getTextStyle-Text--StyledTextComponent-components--PropertiesValue-components--propertiesValueStyles e1d9wgme0',
}

# Настройки Selenium (управление браузером)
SELENIUM_SETTINGS = {
    'headless': True,           # True = браузер невидим (быстрее), False = виден (для отладки)
    'window_size': '1920,1080', # Размер окна браузера
    'implicitly_wait': 3,       # Максимальное время ожидания элементов (сек)
    'page_load_timeout': 20,    # Таймаут загрузки страницы (сек)
}

# Задержки между действиями (оптимизация скорости)
DELAYS = {
    'between_requests': 1,      # Пауза между запросами к разным моделям
    'after_click': 1.5,         # Пауза после клика по ссылке
    'after_search': 1.5,        # Пауза после загрузки результатов поиска
    'after_properties': 1,      # Пауза после загрузки страницы характеристик
}

# Настройки повторных попыток при ошибках
RETRY = {
    'max_attempts': 2,          # Максимальное число попыток
    'delay_between': 1,         # Задержка между попытками (сек)
}

# Настройки логирования
LOGGING = {
    'enabled': True,           # Включить логирование
    'log_dir': 'logs',         # Папка для логов
    'console_level': 'INFO',   # Уровень для консоли (DEBUG, INFO, WARNING, ERROR)
    'file_level': 'DEBUG',     # Уровень для файла
    'max_files': 30,           # Максимальное количество файлов логов
}