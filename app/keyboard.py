from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, CopyTextButton


cmd_start_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = '🖥 Подключится'), KeyboardButton(text='💳 Оплатить доступ')],
    [KeyboardButton(text='🆘 Тех поддержка'), KeyboardButton(text='ℹ️ Статус')],
], resize_keyboard=True)

install_app_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Скачать IOS 🍏', url='https://apps.apple.com/ru/app/happ-proxy-utility-plus/id6746188973'),
    InlineKeyboardButton(text='Подключить IOS 🍏', callback_data='tel_1')],
    [InlineKeyboardButton(text='Скачать Android 📱',url='https://play.google.com/store/apps/details?id=com.happproxy&hl=ru&pli=1'),
    InlineKeyboardButton(text='Подключить Android 📱', callback_data='tel_1')],
    [InlineKeyboardButton(text='Скачать Windows 💻', url='https://github.com/Happ-proxy/happ-desktop/releases/latest/download/setup-Happ.x64.exe'),
    InlineKeyboardButton(text='Подключить Windows 💻', callback_data='tel_1')],
    [InlineKeyboardButton(text='Скачать Mac OS 🍏', url='https://apps.apple.com/ru/app/happ-proxy-utility-plus/id6746188973'),
    InlineKeyboardButton(text='Подключить MacOS 🍏', callback_data='tel_1')],
    [InlineKeyboardButton(text='🆘 Видеоинструкция', callback_data='video_inf')]
    ])

install_app_step = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Подключиться 🚀', callback_data='install_app')]])

buy_sub_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💳 1 мес | 150р', callback_data='buy_sub_1')],
    [InlineKeyboardButton(text='💳 3 мес | 450р', callback_data='buy_sub_3')],
    [InlineKeyboardButton(text='💳 6 мес | 900р', callback_data='buy_sub_6')],
    [InlineKeyboardButton(text='💳 12 мес | 1800р', callback_data='buy_sub_12')],
     ])

def sos_kb(id1):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Тех поддержка', url=f'tg://resolve?domain=Kurbanali567&text=ID пользователя:{id1}')], ])

def check_pay(url, payment_id, mons):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '💳 Оплатить', url=f'{url}')], [InlineKeyboardButton(text = 'Проверить оплату', callback_data=f'pay_{payment_id}_{mons}')]])

def copy(x):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Копировать', copy_text=CopyTextButton(text=x)),]])
