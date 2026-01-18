from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


cmd_start_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = '🖥 Подключится'), KeyboardButton(text='💳 Оплатить доступ')],
    [KeyboardButton(text='ℹ️ Статус'), KeyboardButton(text='❓ Помощь')],
], resize_keyboard=True)

install_app_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Скачать IOS 🍏', url='https://apps.apple.com/ru/app/v2raytun/id6476628951'),
    InlineKeyboardButton(text='Подключить IOS 🍏', callback_data='tel_1')],
    [InlineKeyboardButton(text='Скачать Android 🤖',url='https://play.google.com/store/apps/details?id=com.happproxy&hl=ru&pli=1'),
    InlineKeyboardButton(text='Подключить Android 🤖', callback_data='tel_1')],
    [InlineKeyboardButton(text='Скачать Windows 🖥', url='https://github.com/hiddify/hiddify-app/releases/latest/download/Hiddify-Windows-Setup-x64.Msix'),
    InlineKeyboardButton(text='Подключить Windows ', callback_data='tel_1')],
    ])

install_app_step = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Подключиться 🚀', callback_data='install_app')]])
sos_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Тех поддержка', url='http://t.me/kurbanali567')], ])

buy_sub_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💳 1 мес | 150р', callback_data='buy_sub_1')],
    [InlineKeyboardButton(text='💳 3 мес | 450р', callback_data='buy_sub_3')],
    [InlineKeyboardButton(text='💳 6 мес | 900р', callback_data='buy_sub_6')],
    [InlineKeyboardButton(text='💳 12 мес | 1800р', callback_data='buy_sub_12')],
     ])

def connect(subId, option):
    if option == 'windows':
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Подключить', url=f'https://app.klexvpn.com/?url=hiddify://import/http://148.253.215.32:2096/sub/{subId}')]])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Подключить', url=f'https://testfind2.musacrm.ru/link.php?url_ha=http://148.253.215.32:2096/sub/{subId}')]])

def check_pay(url, payment_id, mons):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '💳 Оплатить', url=f'{url}')], [InlineKeyboardButton(text = 'Проверить оплату', callback_data=f'pay_{payment_id}_{mons}')]])
