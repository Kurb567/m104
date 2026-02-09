from aiogram import types, F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from yookassa import Configuration, Payment

import app.keyboard as kb
import config as x
import requests 
import json 
import uuid
import random 
import time


router = Router()
URL_PANEL_GERMAN = x.URL_PANEL_GERMAN
URL_PANEL_POLAND = x.URL_PANEL_POLAND
URL_PANEL_NEEDERLAND = x.URL_PANEL_NEEDERLAND
USER_NAME_PANEL = x.USER_NAME_PANEL
PANEL_PASSWORD = x.PANEL_PASSWORD
Configuration.configure(x.SHOP_ID, x.SECRET_KEY)
IP_POLAND = x.IP_POLAND
IP_GERMAN = x.IP_GERMAN
IP_NEEDERLAND = x.IP_NEEDERLAND

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
    session.post(f"{URL_PANEL_NEEDERLAND}/login", data={"username": USER_NAME_PANEL, "password": PANEL_PASSWORD})
    data = {
    "id": 0,  # 0 для нового инбаунда
    "userId": tgId,
    "up": 0,
    "down": 0,
    "total": 0,
    "allTime": 0,
    "remark": "",
    "enable": True,
    "expiryTime": 0,
    "trafficReset": "never",
    "lastTrafficResetTime": 0,
    "listen": "",
    "port": PORT,
    "protocol": "vless",
    "settings": json.dumps({
        "clients": [
            {
                "id": tgId,
                "security": "",
                "password": "",
                "flow": "xtls-rprx-vision",
                "email": tgId,  # email пользователя
                "limitIp": 0,
                "totalGB": 0,
                "expiryTime": expiryTime,  # время истечения
                "enable": True,
                "tgId": tgId,
                "subId": f'{tgId}-{PORT}',
                "comment": "",
                "reset": 0,
                "created_at": int(time.time() * 1000),
                "updated_at": int(time.time() * 1000)
            }
        ],
        "decryption": "none",
        "encryption": "none",
        "testseed": [900, 500, 900, 256]
    }, ensure_ascii=False),
    "streamSettings": json.dumps({
        "network": "tcp",
        "security": "reality",
        "externalProxy": [],
        "realitySettings": {
            "show": False,
            "xver": 0,
            "target": "api.vk.ru:443",
            "serverNames": ["api.vk.ru"],
            "privateKey": "AMKU-qwbEL9I-HgmFJyN_wWb0OCeGB3WMkDlvG6eT2g",
            "minClientVer": "",
            "maxClientVer": "",
            "maxTimediff": 0,
            "shortIds": [
                "30288ee8", "4d", "b81ef2", "4b9d", "fbe9984473bb",
                "5c8a987746627fa3", "e622c3039e", "5185906a2999da"
            ],
            "mldsa65Seed": "",
            "settings": {
                "publicKey": "MnNd4UgtPfmeBLDcYGUunP9CkdauibvF8Bb9owlyFFQ",
                "fingerprint": "chrome",
                "serverName": "",
                "spiderX": "/",
                "mldsa65Verify": ""
            }
        },
        "tcpSettings": {
            "acceptProxyProtocol": False,
            "header": {
                "type": "none"
            }
        }
    }, ensure_ascii=False),
    "tag": "inbound-443",
    "sniffing": json.dumps({
        "enabled": False,
        "destOverride": ["http", "tls", "quic", "fakedns"],
        "metadataOnly": False,
        "routeOnly": False
    }, ensure_ascii=False),
    "clientStats": [
        {
            "id": int(tgId),
            "inboundId": 0,
            "enable": True,
            "email": tgId,
            "uuid": tgId,
            "subId": f'{tgId}-{PORT}',
            "up": 0,
            "down": 0,
            "allTime": 0,
            "expiryTime": expiryTime,
            "total": 0,
            "reset": 0,
            "lastOnline": 0
        }
    ]}

    response = session.post(f"{URL_PANEL_NEEDERLAND}/panel/api/inbounds/add", json=data)
    print(response.text)
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
    

    url = URL_PANEL_NEEDERLAND
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

def user_info(id1, option):

    url = URL_PANEL_POLAND
    session = requests.Session()
    session.post(f"{url}/login", data={"username": USER_NAME_PANEL, "password": PANEL_PASSWORD})
    r = session.get(f"{url}/panel/api/inbounds/list").json()
    for i in range(10000):
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
        text = f"""💳 Оформление продления \n\n⏱️ Срок: {int(mons)*30} дней\n💰 Стоимость: {int(mons)*150} RUB\n\nНажмите кнопку «💳 Оплатить» ниже, чтобы перейти к оплате.\n\nID операции: <code>{payment_id}</code>\n<blockquote>После оплаты нажмите <b>Проверить оплату</b></blockquote>"""
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
    <blockquote>🇳🇱 NEEDERLAND Белые списки</blockquote>
    <code>vless://{callback_query.message.chat.id}@{IP_NEEDERLAND}:{PORT}?type=tcp&encryption=none&security=reality&pbk=MnNd4UgtPfmeBLDcYGUunP9CkdauibvF8Bb9owlyFFQ&fp=chrome&sni=api.vk.ru&sid=30288ee8&spx=%2F&flow=xtls-rprx-vision#🇳🇱 NEEDERLAND Белые списки</code>
""", parse_mode="HTML")
