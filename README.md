🛒 Citilink Parser + Telegram Bot

<div align="center">

Автоматический сбор характеристик, цен и изображений товаров с Citilink + управление через Telegram

</div>

⸻

📚 Содержание

* ✨ Возможности⁠￼
* 🛠️ Технологии⁠￼
* 📁 Структура проекта⁠￼
* ⚙️ Установка⁠￼
* 🔐 Настройка ⁠￼.env⁠￼
* 🚀 Запуск⁠￼
* 🤖 Работа с ботом⁠￼
* 📊 Результаты⁠￼
* 🐛 Устранение ошибок⁠￼
* 📝 Логирование⁠￼

⸻

## ✨ Возможности

| Возможность |	Описание |
|-------------|----------|
|🤖 Telegram Bot | Полное управление через Telegram|
|🔎 Поиск товаров | Автоматический поиск моделей|
|📋 Сбор характеристик | Получение всех технических данных|
|💰 Получение цены | Актуальные цены товара|
|🖼️ Изображения | Получение URL изображения|
|📄 Экспорт JSON | Структурированные данные|
|📊 Экспорт CSV	 | Открытие в Excel|
|📤 Отправка файлов | 	Автоматическая отправка результатов|
|📝 Логирование  | 	Подробный журнал работы|
|⚡ Оптимизация  | 	Headless + ускоренный режим|

⸻

## 🛠️ Технологии

|Компонент | Использование|
|----------|--------------|
|Python 3.9+ | Основной язык|
|Aiogram 3.x | Telegram Bot|
|Selenium | Работа с браузером|
|BeautifulSoup | Парсинг HTML|
|Pydantic | Валидация данных|
|aiohttp | Асинхронные запросы|
|tenacity | Повторные попытки|
|dotenv | Конфигурация|
|lxml | Быстрый HTML-парсер|

⸻

## 📁 Структура проекта
```
parsing-citilink
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── pyproject.toml
│
├── main.py
│
├── src/
│   ├── config.py
│   ├── logger.py
│   ├── models.py
│   ├── parser.py
│   └── utils.py
│
├── app/
│   ├── handlers.py
│   └── keyboars.py
│
├── output/
│   ├── results.json
│   └── results.csv
│
└── logs/
    ├── CitilinkParser.log
    └── CitilinkParser_errors.log
```
⸻

## ⚙️ Установка

#### 1. Клонирование
```bash
git clone https://github.com/holomolo4884/citilink-parser.git
cd citilink-parser
```
⸻

#### 2. Виртуальное окружение

##### Windows
```bash
python -m venv venv
venv\Scripts\activate
```
##### Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
```
⸻

#### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```
⸻

## 🔐 Настройка .env

#### Создайте файл:
```bash
cp example.env .env
```
#### Пример:
```
TOKEN=ваш_токен
WORKER_URL=https://worker.workers.dev
HEADLESS=true
PAGE_LOAD_TIMEOUT=60
IMPLICITLY_WAIT=10
DELAY_BETWEEN_REQUESTS=2
LOG_LEVEL=INFO
```
⸻

## 🚀 Запуск
```bash
python main.py
```
#### После запуска:
```
✅ Бот подключён
🔄 Запущен polling
```
⸻

## 🤖 Работа с ботом

#### Команды

|Команда | Назначение|
|--------|-----------|
|/start	| Главное меню|
|/help | Помощь|
|/set_models | Добавить модели|
|/parse | Начать парсинг|
|/get_files | Получить результаты|

⸻

## Примеры ввода моделей

#### В столбик
```
Gorenje ECT643SYB
Gorenje ECT641BCSC
Candy CHXC64TDB
```
#### Через запятую
```
Gorenje ECT643SYB, Candy CHXC64TDB
```
#### Через ;
```
Gorenje ECT643SYB;
Candy CHXC64TDB
```
⸻

## 📊 Результаты

#### После выполнения:

|Файл | Назначение|
|-----|-----------|
|results.json | Все характеристики|
|results.csv | Таблица для Excel|

⸻

## Пример JSON
```json
{
  "Бренд":"GORENJE",
  "Модель":"ECT643SYB",
  "Цена":"31999",
  "Тип конфорок":"Hi-Light",
  "Количество":"4"
}
```

⸻

## 📝 Логирование

#### Логи:
```
logs/
├── CitilinkParser.log
└── CitilinkParser_errors.log
```
#### Пример:
```
[06:14:18] INFO 🚀 ЗАПУСК
[06:16:48] INFO ✅ GORENJE ECT643SYB
[06:17:02] INFO 📄 Файл создан
```
⸻

## 📄 Лицензия

#### MIT License

⸻

## 👨‍💻 Автор

holomolo4884

⸻

<div align="center">

⭐ Если проект оказался полезен — поставьте звезду на GitHub

</div>