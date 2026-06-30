from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Создаем кнопки
button_set_models = KeyboardButton(text='Ввести модели')
button_parse = KeyboardButton(text='Начать парсинг')
button_about = KeyboardButton(text='О нас')
button_contacts = KeyboardButton(text='Контакты')

# Располагаем кнопки в рядах
main = ReplyKeyboardMarkup(
    keyboard=[
        [button_set_models],
        [button_parse],
        [button_about, button_contacts]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню'
)