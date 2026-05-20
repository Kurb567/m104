from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, CopyTextButton


cmd_start_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = '🖥 Подключится'), KeyboardButton(text='💳 Оплатить доступ')],
    [KeyboardButton(text='🆘 Тех поддержка'), KeyboardButton(text='ℹ️ Статус')],
], resize_keyboard=True)

install_app_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Скачать Приложение', url='https://happ.su')],
    [InlineKeyboardButton(text='Подключить подписку', callback_data='tel_1')],
    [InlineKeyboardButton(text='Устройства', callback_data='devices')]
    ])

install_app_step = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Подключиться 🚀', callback_data='install_app')]])

buy_sub_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💳 1 мес | 150р', callback_data='buy_sub_1')],
    [InlineKeyboardButton(text='💳 3 мес | 450р', callback_data='buy_sub_3')],
    [InlineKeyboardButton(text='💳 6 мес | 900р', callback_data='buy_sub_6')],
    [InlineKeyboardButton(text='💳 12 мес | 1800р', callback_data='buy_sub_12')],
    [InlineKeyboardButton(text='💳 200 ГБ | 60р', callback_data='buy_200_gb')],
    [InlineKeyboardButton(text='💳 500 ГБ | 150р', callback_data='buy_500_gb')],
    [InlineKeyboardButton(text='💳 1000 ГБ | 300р', callback_data='buy_1000_gb')],
     ])

def sos_kb(id1):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Тех поддержка', url=f'tg://resolve?domain=Kurbanali567&text=ID пользователя:{id1}')], ])

def check_pay(url, payment_id, mons):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '💳 Оплатить', url=f'{url}')]])

def copy(x):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Копировать', copy_text=CopyTextButton(text=x)),]])

def status_kb(x):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Открыть ссылку', url=x),]])
    