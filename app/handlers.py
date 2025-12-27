from aiogram.filters import CommandStart
from yookassa import Configuration, Payment
from aiogram.types import Message, CallbackQuery
from aiogram import types, F, Router, Bot
import app.keyboard as kb
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
import config as x
import requests
import json
import uuid
import random
import time
import sqlite3


router = Router()
SHOP_ID = x.SHOP_ID
SECRET_KEY = x.SECRET_KEY
Configuration.configure(SHOP_ID, SECRET_KEY)
URL_PANEL = x.URL_PANEL
USER_NAME_PANEL = x.USER_NAME_PANEL
PANEL_PASSWORD = x.PANEL_PASSWORD

def create_payment(amount, description, return_url):
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url
        },
        "capture": True,
        "description": description
    }, idempotence_key)
    return payment.confirmation.confirmation_url, payment.id

def check_payment_status(payment_id):
    payment = Payment.find_one(payment_id)
    if payment.status == 'waiting_for_capture':
        pass
    elif payment.status == 'succeeded':
        return "Оплата успешно завершена!"
    elif payment.status == 'canceled':
        return "Оплата отменена."
    elif payment.status == 'pending':
        return "Ожидание оплаты пользователем..."
    return payment.status

def get_data(user_id, name):
    session = requests.Session()
    response = session.post(f"{URL_PANEL}/login", data={"username": USER_NAME_PANEL, "password": PANEL_PASSWORD})
    print(response.status_code)
    response = session.get(f'{URL_PANEL}/panel/api/inbounds/list')
    print(response.status_code)
    y = response.json()
    t = 0
    for i in range(1000):
        email_value = y['obj'][i]['clientStats'][0]['email']
        if email_value == user_id:
            t=i
            break 
    print(t)        
    sub = y['obj'][t]['clientStats'][0]['subId']   
    add_user_db(user_id, name, sub)
def add_user_db(user_id, name, sub):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER not null primary key, user_id TEXT, name TEXT, sub TEXT)")
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (user_id, name, sub) VALUES (:user_id, :name, :sub)", {'user_id': user_id, 'name': name, 'sub':sub})
def add_user(mons, tgId, first_name):
    duration_days = 3
    duration_days *= mons
    expiryTime = int((time.time() + duration_days * 24 * 60 * 60) * 1000)
    session = requests.Session()
    session.post(f"{URL_PANEL}/login", data={"username": USER_NAME_PANEL, "password": PANEL_PASSWORD})
    data = {
        "up": 0,
        "down": 0,
        "total": 0,
        "remark": first_name,
        "enable": True,
        "expiryTime": 0,
        "port": 443,  # новый порт
        "protocol": "vless",
        "settings": json.dumps({
            "clients": [{
                "id": tgId,
                "email": tgId,
                "limitIp": 2,
                "totalGB": mons*1024 *1024*1024*200,
                "expiryTime": expiryTime,
                "enable": True,
                "tgId": str(uuid.uuid4()),
                "subId": str(uuid.uuid4())
            }],
            "decryption": "none",
            "fallbacks": []
        }),
        
        "streamSettings": json.dumps({
            "network": "ws",
            "security": "tls",
            "tlsSettings": {
                "serverName": "vpnhapp.online",
                "certificates": [
                    {
                        "certificateFile": "/root/cert/vpnhapp.online/fullchain.pem",
                        "keyFile": "/root/cert/vpnhapp.online/privkey.pem"

                    }
                ],
                "alpn": ["http/1.1"]
            },
            "wsSettings": {
                "path": "/",
                "headers": {
                    "Host": "vpnhapp.online"
                }
            }
        }),
        "sniffing": json.dumps({
            "enabled": True,
            "destOverride": ["http", "tls"]
        })
    }
       
    response = session.post(f"{URL_PANEL}/panel/api/inbounds/add", json=data)
    if response.json()['success']:
        session.close()
        return [tgId, first_name]
    else:
        #print(response.json()['msg'])
        session.close()
        return [0, 0]       
def start(ex_time, id, name):
    x = add_user(ex_time, id, name)   
    if x[0] == 0 and x[1] == 0:
        return 10/0  
    user_id = x[0]
    name = x[1]
    get_data(user_id, name)

def start_update(mons, id1):
    x1 = None
    x2 = None
    url = URL_PANEL
    session = requests.Session()
    session.post(f"{url}/login", data={"username": USER_NAME_PANEL, "password": PANEL_PASSWORD})
    
    duration_days = 30
    duration_days *= mons
    totalGB1 = mons*1024 *1024*1024*200 
    ex_time_1 = ((duration_days * 24 * 60 * 60) * 1000)

    r = session.get(f"{url}/panel/api/inbounds/list").json()
    for i in range(100):
        if r['obj'][i]['clientStats'][0]['email'] == id1:
            x = r['obj'][i] 
            break
        
    settings = json.loads(x['settings'])
    ex_time_2 = settings['clients'][0]['expiryTime']
    totalGB = settings['clients'][0]['totalGB']
    del settings      

    ex_time = ex_time_2 + ex_time_1
    settings = json.loads(x['settings'])
    
    
    
    settings['clients'][0]['expiryTime'] = ex_time
    settings['clients'][0]['totalGB'] = totalGB + totalGB1
    x['settings'] = json.dumps(settings)
    #  x['clientStats'][0]['email'] = 0
    x['clientStats'][0]['expiryTime'] = ex_time
    x['clientStats'][0]['totalGB'] = totalGB + totalGB1
    
    print(x)
    session.post(f"{url}/panel/api/inbounds/update/50", json=x)
    session.close()
        
def user_info(id1, option):
    url = URL_PANEL
    session = requests.Session()
    session.post(f"{url}/login", data={"username": USER_NAME_PANEL, "password": PANEL_PASSWORD})
    r = session.get(f"{url}/panel/api/inbounds/list").json()
    for i in range(1000):
        if r['obj'][i]['clientStats'][0]['email'] == id1:
            x1 = r['obj'][i]['clientStats'][0]['subId']
            x2 = r['obj'][i]['port']
            x = r['obj'][i] 
            x2 = i
            break
    if option == 2:
        return x1
    if option == 3:
        return x2    
    settings = json.loads(x['settings'])
    ex_time = settings['clients'][0]['expiryTime']
    del settings
    session.close()
    current_time_ms = int(time.time() * 1000)
    time_diff_ms = ex_time - current_time_ms
    if time_diff_ms <= 0:
        return "Время истекло"
    total_seconds = time_diff_ms // 1000
    days = total_seconds // (24 * 60 * 60)
    remaining_seconds = total_seconds % (24 * 60 * 60)
    hours = remaining_seconds // (60 * 60)
    remaining_seconds %= (60 * 60)
    minutes = remaining_seconds // 60
    return f'{days} дней, {hours} часов, {minutes} минут'
    
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'Добрый день, {message.chat.first_name}!', reply_markup=kb.cmd_start_kb)
    try:
        start(1, str(message.chat.id), str(message.chat.first_name))
        await message.answer('Ваш новый аккаунт активирован! У вас есть бесплатный тестовый период на 3 дня. Нажмите ниже, чтобы подключиться и начать пользоваться сервисом', reply_markup=kb.install_app_step)
    except ZeroDivisionError:
        await message.answer(f'Вы успешно зарегистрированы у вас осталось \n<b>{user_info(str(message.chat.id), 1)}</b>', parse_mode='HTML') 
    except TypeError: pass

@router.message(F.text == '🖥 Подключится')
async def install_app(message: Message):
    x=f"""<b>Подключение к VPN происходит в 2 шага:</b>\n <blockquote>1. Кнопка "Скачать" - для загрузки приложения\n2. Кнопка "Подключить" - для добавления локаций</blockquote>\n\n🍏 iOS - iPhone, iPad и Mac\n🤖 - все устройства Android\n🖥 - ПК и ноутбуки Windows\n\n<i>Ссылка для ручного подключения, нажмите чтобы скопировать в буфер ↓</i>\n<code>http://148.253.215.32:2096/sub/{user_info(str(message.chat.id), 2)}</code>"""
    await message.answer(x, parse_mode='HTML', reply_markup=kb.install_app_kb)

@router.message(F.text == 'ℹ️ Статус')
async def profil(message: Message):
    await message.answer(f"До окончании подписки осталось: <blockquote>{user_info(str(message.chat.id), 1)}</blockquote>", parse_mode='HTML')    

@router.message(F.text == '❓ Помощь')
async def sos(message: Message):
    await message.answer('❓ Помощь', reply_markup=kb.sos_kb)

@router.callback_query(F.data == 'install_app')
async def install_app(callback_query: CallbackQuery):
    x=f"""<b>Подключение к VPN происходит в 2 шага:</b>\n <blockquote>1. Кнопка "Скачать" - для загрузки приложения\n2. Кнопка "Подключить" - для добавления локаций</blockquote>\n\n🍏 iOS - iPhone, iPad и Mac\n🤖 - все устройства Android\n🖥 - ПК и ноутбуки Windows\n\n<i>Ссылка для ручного подключения, нажмите чтобы скопировать в буфер ↓</i>\n<code>http://148.253.215.32:2096/sub/{user_info(str(callback_query.message.chat.id), 2)}</code>"""
    await callback_query.message.answer(x, parse_mode='HTML', reply_markup=kb.install_app_kb)

@router.message(F.text == '💳 Оплатить доступ')
async def buy_sub(message: Message):
    text = """Ваше подключение можно использовать на двух своих устройствах одновременно.
Выберите оптимальный для вас тариф:

<blockquote>💳 Можно оплатить приложением банка, СБП и картой МИР</blockquote>"""
    await message.answer(text, parse_mode="HTML", reply_markup=kb.buy_sub_kb)

@router.message(F.text == 'Пользователи')
async def users(message: Message):
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * from users")
    x = c.fetchall()
    text = ''
    for i in x:
        text += f'{i[0]} {i[1]} {i[2]}\n'
    await message.answer(text)
   
      
class Buy_Sub:
    @router.callback_query(F.data.startswith('buy_sub_'))
    async def buy_sub_(callback_query: CallbackQuery):
        mons = callback_query.data[-1]
        
        if mons == '2':
            mons = '12'
        rub = f'{int(mons)*150}.00'  
        url, payment_id = create_payment(rub, "vpn", "https://t.me/HappPlus_bot")
        text = f"""💳 Оформление продления

⏱️ Срок: {int(mons)*30} дней
📱 Лимит устройств: 2
💰 Стоимость: {int(mons)*150} RUB

Нажмите кнопку «💳 Оплатить» ниже, чтобы перейти к оплате.

ID операции: <code>{payment_id}</code>
<blockquote>После оплаты нажмите <b>Проверить оплату</b></blockquote>"""
        await callback_query.message.answer(text, reply_markup=kb.check_pay(url, payment_id, mons))
        
    @router.callback_query(F.data.startswith('pay_'))
    async def check_pay(callback_query: CallbackQuery):
        x = callback_query.data.split('_')
        mons = x[2]
        payment_id = x[1]
        if mons == '2':
            mons = '12' 
        x = check_payment_status(payment_id)
        if x == 'Оплата успешно завершена!':
            try: start(int(mons), str(callback_query.message.chat.id), str(callback_query.message.chat.first_name))
            except ZeroDivisionError as e: start_update(int(mons), str(callback_query.message.chat.id)) 
            except TypeError: pass 
            await callback_query.message.edit_text('✅ Подписка продлена')
        else: 
            await callback_query.message.answer(f'{x}')

class connect_device:
    @router.callback_query(F.data == 'desktop_1')
    async def desktop_1(callback_query: CallbackQuery):
        await callback_query.message.answer(f"Нажмите ниже: если приложение уже установлено", parse_mode="HTML", reply_markup=kb.connect(callback_query.message.chat.id, user_info(str(callback_query.message.chat.id), 2), 'windows'))
    
    @router.callback_query(F.data == 'tel1')
    async def tel_1(callback_query: CallbackQuery):
        await callback_query.message.answer("Нажмите ниже: если приложение уже установлено", reply_markup=kb.connect(callback_query.message.chat.id, user_info(str(callback_query.message.chat.id), 2), 'tel'))
