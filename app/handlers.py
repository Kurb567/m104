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
URL_PANEL_GERMAN = x.URL_PANEL_GERMAN
URL_PANEL_POLAND = x.URL_PANEL_POLAND
Configuration.configure(x.SHOP_ID, x.SECRET_KEY)
USER_NAME_PANEL = x.USER_NAME_PANEL
PANEL_PASSWORD = x.PANEL_PASSWORD
IP_POLAND = x.IP_POLAND
IP_GERMAN = x.IP_GERMAN

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

def add_user(mons, tgId, first_name):
    duration_days = 30
    duration_days *= mons
    expiryTime = int((time.time() + duration_days * 24 * 60 * 60) * 1000)
    PORT = random.randint(40, 10000)
    
    session = requests.Session()
    session.post(f"{URL_PANEL_GERMAN}/login", data={"username": USER_NAME_PANEL, "password": PANEL_PASSWORD})
    data = {
        "up": 0,
        "down": 0,
        "total": 0,
        "remark": first_name,
        "enable": True,
        "expiryTime": 0,
        "port": PORT,  # новый порт
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
                "serverName": '148.253.215.32',
                "certificates": [
                    {
                        "certificateFile": "/root/cert/ip/fullchain.pem",
                        "keyFile": "/root/cert/ip/privkey.pem"

                    }
                ],
                "alpn": ["http/1.1"]
            },
            "wsSettings": {
                "path": "/",
                "headers": {
                    "Host": '148.253.215.32'
                }
            }
        }),
        "sniffing": json.dumps({
            "enabled": True,
            "destOverride": ["http", "tls"]
        })
    }
       
    response = session.post(f"{URL_PANEL_GERMAN}/panel/api/inbounds/add", json=data)
#------------
    session = requests.Session()
    session.post(f"{URL_PANEL_POLAND}/login", data={"username": USER_NAME_PANEL, "password": PANEL_PASSWORD})
    data = {
        "up": 0,
        "down": 0,
        "total": 0,
        "remark": first_name,
        "enable": True,
        "expiryTime": 0,
        "port": PORT,  # новый порт
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
                "serverName": '148.253.212.139',
                "certificates": [
                    {
                        "certificateFile": "/root/cert/ip/fullchain.pem",
                        "keyFile": "/root/cert/ip/privkey.pem"

                    }
                ],
                "alpn": ["http/1.1"]
            },
            "wsSettings": {
                "path": "/",
                "headers": {
                    "Host": '148.253.212.139'
                }
            }
        }),
        "sniffing": json.dumps({
            "enabled": True,
            "destOverride": ["http", "tls"]
        })
    }
       
    response = session.post(f"{URL_PANEL_POLAND}/panel/api/inbounds/add", json=data)
    
    if response.json()['success']:
        session.close()
        return [tgId, first_name]
    else:
        #print(response.json()['msg'])
        session.close()
        return 10/0       


def start_update(mons, id1):
    url = URL_PANEL_POLAND
    session = requests.Session()
    session.post(f"{url}/login", data={"username": USER_NAME_PANEL, "password": PANEL_PASSWORD})
    
    duration_days = 30
    duration_days *= mons
    totalGB1 = mons*1024 *1024*1024*200 
    ex_time_1 = ((duration_days * 24 * 60 * 60) * 1000)

    r = session.get(f"{url}/panel/api/inbounds/list").json()
    for i in range(10000):
        if r['obj'][i]['clientStats'][0]['email'] == id1:
            x = r['obj'][i] 
            break
        
    settings = json.loads(x['settings'])
    ex_time_2 = settings['clients'][0]['expiryTime']
    totalGB = settings['clients'][0]['totalGB']
    del settings      
    if ex_time_2 < time.time():
        ex_time_2 = time.time()
    ex_time = ex_time_2 + ex_time_1
    settings = json.loads(x['settings'])
    
    settings['clients'][0]['expiryTime'] = ex_time
    settings['clients'][0]['totalGB'] = totalGB + totalGB1
    x['settings'] = json.dumps(settings)
    x['clientStats'][0]['expiryTime'] = ex_time
    x['clientStats'][0]['totalGB'] = totalGB + totalGB1
    print(f"{x['clientStats'][0]['id']}")
    session.post(f"{url}/panel/api/inbounds/updateClient/{id1}", json=x)
    session.close()
    
    url = URL_PANEL_GERMAN
    session = requests.Session()
    session.post(f"{url}/login", data={"username": USER_NAME_PANEL, "password": PANEL_PASSWORD})
    
    duration_days = 30
    duration_days *= mons
    totalGB1 = mons*1024 *1024*1024*200 
    ex_time_1 = ((duration_days * 24 * 60 * 60) * 1000)

    r = session.get(f"{url}/panel/api/inbounds/list").json()
    for i in range(10000):
        if r['obj'][i]['clientStats'][0]['email'] == id1:
            x = r['obj'][i] 
            break
        
    settings = json.loads(x['settings'])
    ex_time_2 = settings['clients'][0]['expiryTime']
    totalGB = settings['clients'][0]['totalGB']
    del settings      
    if ex_time_2 < time.time():
        ex_time_2 = time.time()
    ex_time = ex_time_2 + ex_time_1
    settings = json.loads(x['settings'])
    
    settings['clients'][0]['expiryTime'] = ex_time
    settings['clients'][0]['totalGB'] = totalGB + totalGB1
    x['settings'] = json.dumps(settings)
    x['clientStats'][0]['expiryTime'] = ex_time
    x['clientStats'][0]['totalGB'] = totalGB + totalGB1
    session.post(f"{url}/panel/api/inbounds/updateClient/{id1}", json=x)
    session.close()
        
def user_info(id1, option):
   
    url = URL_PANEL_POLAND
    session = requests.Session()
    session.post(f"{url}/login", data={"username": USER_NAME_PANEL, "password": PANEL_PASSWORD})
    r = session.get(f"{url}/panel/api/inbounds/list").json()
    for i in range(1000):
        if r['obj'][i]['clientStats'][0]['email'] == id1:
            x1 = r['obj'][i]['clientStats'][0]['subId']
            x2 = r['obj'][i]['port']
            x = r['obj'][i] 
            break
    if option == 2:
        return x1
    elif option == 3:
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

class Nav:   
    @router.message(CommandStart())
    async def cmd_start(message: Message):
        await message.answer(f'Добрый день, {message.chat.first_name}!', reply_markup=kb.cmd_start_kb)
        try:
            add_user(0.1, str(message.chat.id), str(message.chat.first_name))
            await message.answer('Ваш новый аккаунт активирован! У вас есть бесплатный тестовый период на 3 дня. Нажмите ниже, чтобы подключиться и начать пользоваться сервисом', reply_markup=kb.install_app_step)
        except ZeroDivisionError:
            await message.answer(f'Вы успешно зарегистрированы у вас осталось \n<b>{user_info(str(message.chat.id), 1)}</b>', parse_mode='HTML') 
        except TypeError: pass

    @router.message(F.text == '🖥 Подключится')
    async def install_app(message: Message):
        x=f"""<b>Подключение к VPN происходит в 2 шага:</b>\n <blockquote>1. Кнопка "Скачать" - для загрузки приложения\n2. Кнопка "Подключить" - для добавления локаций</blockquote>\n\n🍏 iOS - iPhone, iPad и Mac\n🤖 - все устройства Android\n🖥 - ПК и ноутбуки Windows"""
        await message.answer(x, parse_mode='HTML', reply_markup=kb.install_app_kb)

    @router.message(F.text == 'ℹ️ Статус')
    async def profil(message: Message):
        await message.answer(f"До окончании подписки осталось: <blockquote>{user_info(str(message.chat.id), 1)}</blockquote>", parse_mode='HTML')    

    @router.message(F.text == '❓ Помощь')
    async def sos(message: Message):
        await message.answer('❓ Помощь', reply_markup=kb.sos_kb)

    @router.callback_query(F.data == 'install_app')
    async def install_app(callback_query: CallbackQuery):
        x=f"""<b>Подключение к VPN происходит в 2 шага:</b>\n <blockquote>1. Кнопка "Скачать" - для загрузки приложения\n2. Кнопка "Подключить" - для добавления локаций</blockquote>\n\n🍏 iOS - iPhone, iPad и Mac\n🤖 - все устройства Android\n🖥 - ПК и ноутбуки Windows"""
        await callback_query.message.answer(x, parse_mode='HTML', reply_markup=kb.install_app_kb)

    @router.message(F.text == '💳 Оплатить доступ')
    async def buy_sub(message: Message):
        text = """Ваше подключение можно использовать на двух своих устройствах одновременно.
    Выберите оптимальный для вас тариф:

    <blockquote>💳 Можно оплатить приложением банка, СБП и картой МИР</blockquote>"""
        await message.answer(text, parse_mode="HTML", reply_markup=kb.buy_sub_kb)

  
      
class Buy_Sub:
    @router.callback_query(F.data.startswith('buy_sub_'))
    async def buy_sub_(callback_query: CallbackQuery):
        mons = callback_query.data[-1]
        
        if mons == '2':
            mons = '12'
        rub = f'{int(mons)*150}.00'  
        url, payment_id = create_payment(rub, str(callback_query.message.chat.id), "https://t.me/HappPlus_bot")
        text = f"""💳 Оформление продления \n\n⏱️ Срок: {int(mons)*30} дней\n📱 Лимит устройств: 2\n💰 Стоимость: {int(mons)*150} RUB\n\nНажмите кнопку «💳 Оплатить» ниже, чтобы перейти к оплате.\n\nID операции: <code>{payment_id}</code>\n<blockquote>После оплаты нажмите <b>Проверить оплату</b></blockquote>"""
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
            try: add_user(int(mons), str(callback_query.message.chat.id), str(callback_query.message.chat.first_name))
            except ZeroDivisionError as e: start_update(int(mons), str(callback_query.message.chat.id)) 
            except TypeError: pass 
            await callback_query.message.edit_text('✅ Подписка продлена')
        else: 
            await callback_query.message.answer(f'{x}')

   
@router.callback_query(F.data == 'tel_1')
async def tel_1(callback_query: CallbackQuery):
    PORT = user_info(str(callback_query.message.chat.id), 3)
    await callback_query.message.answer(f"""1.Нажмите на ссылку чтобы она скопировалась\n2.Откройте приложение и нажмите плюс в правой верхней части экрана \n<b>3.Выберите импорт из буфера обмена </b>
    <blockquote>🇲🇨 POLAND</blockquote>
    <code>vless://{callback_query.message.chat.id}@{IP_POLAND}:{PORT}?type=ws&encryption=none&path=%2F&host={IP_POLAND}&security=tls&fp=chrome&alpn=http%2F1.1&sni={IP_POLAND}#🇲🇨 POLAND</code> 
    <blockquote>🇩🇪 GERMAN</blockquote>
    <code>vless://{callback_query.message.chat.id}@{IP_GERMAN}:{PORT}?type=ws&encryption=none&path=%2F&host={IP_GERMAN}&security=tls&fp=chrome&alpn=http%2F1.1&sni={IP_GERMAN}#🇩🇪 GERMAN</code>
""", parse_mode="HTML")
