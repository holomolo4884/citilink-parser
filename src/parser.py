# ============================================================
# ОСНОВНОЙ ПАРСЕР
# Использует Selenium для навигации и BeautifulSoup для парсинга
# ============================================================

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from src.config import (
    SELECTORS, SELENIUM_SETTINGS, DELAYS, WAIT_TIMEOUTS,
    USER_AGENT, SEARCH_URL, PRICE_SELECTOR, IMAGE_CONTAINER_SELECTOR
)
from src.models import CooktopProperties
from src.logger import logger
from tenacity import retry, stop_after_attempt, wait_fixed  # Для повторных попыток
import logging

# Отключаем лишние логи (меньше мусора в консоли)
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('webdriver_manager').setLevel(logging.WARNING)


# ============================================================
# ФУНКЦИЯ: СОЗДАНИЕ ДРАЙВЕРА
# ============================================================
def get_driver():
    """
    Создает и настраивает драйвер Chrome.
    - headless режим для скорости
    - отключение картинок для ускорения загрузки
    - минимальные таймауты
    """
    logger.debug("Создание драйвера Chrome...")


    # Создаем объект с настройками Chrome
    chrome_options = Options()
    
    # Запускаем браузер в фоновом режиме (невидимый)
    if SELENIUM_SETTINGS.get('headless', True):
        chrome_options.add_argument("--headless")
        logger.debug("Запуск в headless режиме")

    
    # Оптимизация скорости: отключаем ненужные функции
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    
    # ОТКЛЮЧАЕМ ЗАГРУЗКУ КАРТИНОК (значительно ускоряет загрузку страниц)
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    
    # Маскируем автоматизацию (чтобы сайт не блокировал)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Размер окна и User-Agent
    chrome_options.add_argument(f"--window-size={SELENIUM_SETTINGS.get('window_size', '1920,1080')}")
    chrome_options.add_argument(f"user-agent={USER_AGENT}")
    
    # Автоматически скачиваем и устанавливаем ChromeDriver
    service = Service(ChromeDriverManager().install())
    
    # Создаем драйвер
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Скрываем признак автоматизации (чтобы сайт не догадался)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # Устанавливаем таймауты
    driver.implicitly_wait(SELENIUM_SETTINGS.get('implicitly_wait', 3))
    driver.set_page_load_timeout(SELENIUM_SETTINGS.get('page_load_timeout', 20))

    logger.debug("Драйвер создан успешно")
    return driver


# ============================================================
# ФУНКЦИЯ: ПОИСК ТОВАРА И КЛИК
# ============================================================
@retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
def search_and_click_product(driver, model_name: str) -> str:
    """
    Ищет товар по названию и кликает по первому результату.
    Декоратор @retry делает повторную попытку при ошибке.
    
    Аргументы:
        driver: Selenium WebDriver
        model_name: Название модели (например: "Gorenje ECT643SYB")
    
    Возвращает:
        URL страницы товара или None при ошибке
    """
    # Формируем URL для поиска (заменяем пробелы на +)
    search_url = SEARCH_URL.format(query=model_name.replace(' ', '+'))
    logger.info(f"🔍 Поиск: {model_name}")
    logger.debug(f"URL: {search_url}")
    
    # Открываем страницу поиска
    driver.get(search_url)
    time.sleep(DELAYS['after_search'])  # Ждем загрузки
    
    try:
        # Ждем появления ссылки на товар (максимум 8 секунд)
        # Ищем по CSS-селектору: любая ссылка с /product/ в href
        product_link = WebDriverWait(driver, WAIT_TIMEOUTS['product_link']).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/product/']"))
        )
        
        # Получаем URL товара
        href = product_link.get_attribute("href")
        logger.info(f"✅ Найдена ссылка")
        logger.debug(f"Ссылка: {href}")
        
        # Скроллим к ссылке (чтобы она точно была видна)
        driver.execute_script("arguments[0].scrollIntoView(true);", product_link)
        time.sleep(DELAYS['after_scroll'])
        
        # Кликаем через JavaScript (надежнее, чем обычный click)
        driver.execute_script("arguments[0].click();", product_link)
        time.sleep(DELAYS['after_click'])  # Ждем загрузки страницы товара
        
        logger.info(f"✅ Перешли на страницу товара")
        return driver.current_url  # Возвращаем текущий URL
        
    except TimeoutException:
        logger.error(f"❌ Таймаут при поиске: {model_name}")
        logger.exception(e)
        return None
    except Exception as e:
        logger.error(f"❌ Ошибка при поиске: {model_name}")
        logger.debug(f"Детали: {e}")
        return None


# ============================================================
# ФУНКЦИЯ: ПАРСИНГ ЦЕНЫ И КАРТИНКИ
# ============================================================
def parse_price_and_image(driver) -> tuple:
    """
    Парсит цену и ссылку на изображение со страницы товара.
    Использует BeautifulSoup с парсером lxml (быстрее).
    
    Возвращает:
        (price, image_url) - кортеж из двух значений
    """
    logger.debug("Парсинг цены и картинки")
    
    # Получаем HTML страницы
    html = driver.page_source
    
    # Создаем объект BeautifulSoup с быстрым парсером lxml
    soup = BeautifulSoup(html, 'lxml')
    
    price = None
    image_url = None
    
    # ---------- ПАРСИНГ ЦЕНЫ ----------
    # Ищем по известному CSS-классу цены
    price_element = soup.find('span', class_=lambda c: c and PRICE_SELECTOR in c)
    
    if price_element:
        # Нашли цену по основному классу
        price = price_element.get_text(strip=True)
        logger.info(f"💰 Цена: {price}")
    else:
        # Альтернативный поиск: ищем любые элементы с "price" в классе и "₽" в тексте
        price_elements = soup.find_all('span', class_=lambda c: c and 'price' in str(c).lower())
        for elem in price_elements:
            text = elem.get_text(strip=True)
            if text and '₽' in text:  # Проверяем, что это точно цена
                price = text
                logger.info(f"💰 Цена: {price}")
                break

    if not price:
        logger.warning("⚠️ Цена не найдена")
    
    # ---------- ПАРСИНГ КАРТИНКИ ----------
    # Ищем контейнер с изображениями
    image_container = soup.find('div', class_=lambda c: c and IMAGE_CONTAINER_SELECTOR in c)
    
    if image_container:
        # Нашли контейнер, ищем в нем первую картинку
        img = image_container.find('img')
        if img and img.get('src'):
            image_url = img.get('src')
            logger.debug(f"🖼️ Картинка найдена")
    else:
        # Альтернативный поиск: ищем картинки с product-images в src
        images = soup.find_all('img')
        for img in images:
            src = img.get('src', '')
            if 'product-images' in src:
                image_url = src
                logger.debug(f"🖼️ Картинка найдена")
                break
    
    # Выводим найденное в консоль
    if not image_url:
        logger.warning("⚠️ Картинка не найдена")
    
    return price, image_url


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ТЕКСТА
# ============================================================
def get_deep_text(element) -> str:
    """
    Извлекает весь текст из элемента и всех вложенных элементов.
    Очищает от лишних пробелов и переносов строк.
    """
    if not element:
        return ""
    return ' '.join(element.get_text(strip=True).split())


def get_full_title(title_container) -> str:
    """
    Собирает полный заголовок характеристики.
    Некоторые заголовки разбиты на несколько span-элементов.
    """
    if not title_container:
        return ""
    
    return ' '.join(title_container.get_text(strip=True).split())


# ============================================================
# ФУНКЦИЯ: ПАРСИНГ ХАРАКТЕРИСТИК
# ============================================================
def parse_properties_with_bs4(driver) -> dict:
    """
    Парсит все характеристики товара со страницы /properties/.
    Возвращает словарь {название_характеристики: значение}.
    """
    logger.debug("Парсинг характеристик")
    
    # Получаем HTML и создаем BeautifulSoup с lxml
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    
    properties = {}
    
    # ----- Находим контейнер с характеристиками -----
    # Ищем по уникальному классу списка характеристик
    # Обычно контейнер имеет класс 'app-catalog-li9fsz-components--Properties'
    # Берём первый класс из строки (он уникальный)
    container_class = SELECTORS['properties_container'].split()[0] if SELECTORS['properties_container'] else 'app-catalog-li9fsz-components--Properties'

    # Ищем по первому уникальному классу
    properties_list = soup.find('ul', class_=lambda c: c and container_class in c if c else False)
    
    # Если не нашли - пробуем альтернативный класс
    if not properties_list:
        properties_list = soup.find('ul', class_=lambda c: c and 'propertiesStyles' in c)
    
    # Если контейнер не найден - возвращаем пустой словарь
    if not properties_list:
        logger.warning("⚠️ Контейнер с характеристиками не найден")
        return {}
    
    # ----- Находим все элементы с характеристиками -----
    # Каждая характеристика - это div с уникальным классом
    item_class = SELECTORS['property_item'].split()[0] if SELECTORS['property_item'] else 'app-catalog-7g4f64-Flex'

    property_items = properties_list.find_all('div', class_=lambda c: c and item_class in c if c else False)

    logger.debug(f"Найдено элементов характеристик: {len(property_items)}")

    # Получаем классы для поиска заголовка и значения из SELECTORS
    title_class = SELECTORS['title_container'].split()[0] if SELECTORS['title_container'] else 'app-catalog-61b1vd-Flex'
    value_class = SELECTORS['property_value'].split()[0] if SELECTORS['property_value'] else 'es7ht5z6'
    
    # ----- Проходим по каждой характеристике -----
    for item in property_items:
        # Находим контейнер с заголовком (название характеристики)
        title_container = item.find('div', class_=lambda c: c and title_class in c if c else False)
        
        # Находим элемент со значением
        value_elem = item.find('span', class_=lambda c: c and value_class in c if c else False)
        

        if not value_elem:
            # Альтернативный класс для значения
            value_elem = item.find('span', class_=lambda c: c and 'PropertiesValue' in c)
        
        # Если есть и заголовок, и значение - сохраняем
        if title_container and value_elem:
            # Извлекаем текст
            title_text = get_full_title(title_container)
            value_text = get_deep_text(value_elem)
            
            # Если текст не пустой - добавляем в словарь
            if title_text and value_text:
                properties[title_text] = value_text
                # Логируем первые 40 символов
                logger.debug(f"  {title_text}: {value_text[:40]}...")  

    logger.info(f"📋 Собрано {len(properties)} характеристик")
    return properties


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ ПАРСИНГА
# ============================================================
def parse_cooktop_by_search(model_name: str) -> CooktopProperties:
    """
    Главная функция: собирает все данные о товаре.
    
    Этапы:
    1. Поиск товара и переход на страницу
    2. Парсинг цены и картинки
    3. Переход на страницу характеристик
    4. Парсинг всех характеристик
    5. Сбор данных в модель Pydantic
    
    Аргументы:
        model_name: Название модели для поиска
        
    Возвращает:
        CooktopProperties - объект с данными
    """
    logger.info(f"🚀 Начинаем парсинг: {model_name}")
    

    driver = None
    try:
        # ----- Создаем драйвер -----
        driver = get_driver()
        
        # ----- Ищем товар и переходим на страницу -----
        product_url = search_and_click_product(driver, model_name)
        if not product_url:
            # Если не удалось найти товар - возвращаем пустую модель
            logger.error(f"❌ Товар не найден: {model_name}")
            return CooktopProperties()
        
        # ----- Парсим цену и картинку -----
        price, image_url = parse_price_and_image(driver)
        
        # ----- Переходим на страницу характеристик -----
        # Добавляем /properties/ к URL (убираем слеш в конце, если есть)
        properties_url = product_url.rstrip('/') + '/properties/'
        logger.debug(f"Переход на страницу характеристик: {properties_url}")
        driver.get(properties_url)
        time.sleep(DELAYS['after_properties'])
        
        # ----- Парсим все характеристики -----
        raw_data = parse_properties_with_bs4(driver)
        
        # ----- Добавляем цену и картинку в словарь -----
        raw_data['Цена'] = price
        raw_data['Ссылка на изображение'] = image_url
        

        # ----- Создаем модель Pydantic -----
        cooktop = CooktopProperties(**raw_data)
        
        # ----- Отделяем базовые поля от характеристик -----
        # Базовые поля - всегда есть у всех моделей
        base_fields = {'Бренд', 'Модель', 'Цена', 'Ссылка на изображение'}
        
        # Все остальные поля сохраняем в словарь characteristics
        cooktop.characteristics = {
            key: value for key, value in raw_data.items() 
            if key not in base_fields
        }
        
        logger.info(f"✅ {cooktop.brand} {cooktop.model} — {len(cooktop.characteristics)} хар-к, цена: {price}")
        return cooktop
        
    except Exception as e:
        # Обрабатываем любые ошибки
        logger.error(f"❌ Критическая ошибка при парсинге {model_name}")
        logger.debug(f"Детали: {e}")
        return CooktopProperties()
        
    finally:
        # ----- Закрываем драйвер (освобождаем ресурсы) -----
        if driver:
            driver.quit()
            logger.debug("Драйвер закрыт")


# Алиас для совместимости с другими частями кода
parse_cooktop = parse_cooktop_by_search