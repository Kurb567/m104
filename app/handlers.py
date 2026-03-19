from aiogram import types, F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from yookassa import Configuration, Payment
from marzban import MarzbanAPI, UserCreate
from marzban.models import UserModify
import app.keyboard as kb
import config as x
import json 
import random 
import time


router = Router()
Configuration.configure(x.SHOP_ID, x.SECRET_KEY)
async def get_link(tgId):
    api = MarzbanAPI(base_url="https://ctjkk.duckdns.org:8000")
    token = await api.get_token(username="admin", password="56731096842")
    user = await api.get_user(username=tgId, token=token.access_token)
    return user.subscription_url


async def add_user(mons, tgId):
    duration_days = 3
    duration_days *= int(mons)
    expiryTime = int((time.time() + duration_days * 24 * 60 * 60))
    api = MarzbanAPI(base_url="https://ctjkk.duckdns.org:8000/")
    token = await api.get_token(username="admin", password="56731096842")

    new_user = UserCreate(
        username=str(tgId),
        proxies={"vless": { "flow": "xtls-rprx-vision" }, "trojan":{}, "vmess":{}}, 
        data_limit=200*1024*1024*1024, # 5 ГБ в байтах
        expire=expiryTime)
    try:
        user = await api.add_user(user=new_user, token=token.access_token)
        print(f"Пользователь создан!")
    except Exception as e:
        return 10/0

import datetime

import datetime

import datetime

async def user_info(tgId: str):
    api = MarzbanAPI(base_url="https://ctjkk.duckdns.org:8000")
    try:
        # 1. Авторизация
        token = await api.get_token(username="admin", password="56731096842")
        
        # 2. Попытка получить юзера
        user = await api.get_user(username=tgId, token=token.access_token)
        
        if not user.expire:
            return "Безлимитно"

        # 3. Расчет времени
        now = datetime.datetime.now()
        expire_date = datetime.datetime.fromtimestamp(user.expire)
        delta = expire_date - now

        if delta.total_seconds() <= 0:
            return "Срок подписки истек"

        total_sec = int(delta.total_seconds())
        
        months = total_sec // (30 * 24 * 3600)
        days = (total_sec % (30 * 24 * 3600)) // (24 * 3600)
        hours = (total_sec % (24 * 3600)) // 3600
        minutes = (total_sec % 3600) // 60

        parts = []
        if months > 0: parts.append(f"{months} мес")
        if days > 0: parts.append(f"{days} дн")
        if hours > 0: parts.append(f"{hours} ч")
        if minutes > 0: parts.append(f"{minutes} мин")

        return " ".join(parts) if parts else "меньше минуты"

    except Exception as e:
        # Если API вернуло 404 (Not Found) или другую ошибку
        print(f"Ошибка Marzban API: {e}")
        return "Пользователя нет, введите /start"


async def start_update(add_months, username):
    api = MarzbanAPI(base_url="https://ctjkk.duckdns.org:8000")
    add_gb = add_months * 200
    try:
        token = await api.get_token(username="admin", password="56731096842")
        user = await api.get_user(username=username, token=token.access_token)
        seconds_to_add = add_months * 30 * 24 * 60 * 60
        current_time = int(time.time())
        base_time = max(user.expire or 0, current_time)
        new_expire = base_time + seconds_to_add
        new_limit = user.data_limit
        if add_gb > 0:
            new_limit = (user.data_limit or 0) + (add_gb * 1024**3)
        modify_data = UserModify(
            expire=new_expire,
            data_limit=new_limit,
            status="active" 
        )
        updated_user = await api.modify_user(
            username=username, 
            user=modify_data, 
            token=token.access_token
        )
        return f"Пользователь {username} продлен до: {time.ctime(new_expire)}\n Новый лимит: {updated_user.data_limit / 1024**3:.2f} GB"
    except Exception as e:
        print(f"Ошибка при продлении: {e}")   


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

 

class Nav:   
    @router.message(CommandStart())
    async def cmd_start(message: Message):
        await message.answer(f'Добрый день, {message.chat.first_name}!', reply_markup=kb.cmd_start_kb)
        try:
            await add_user(1, str(message.chat.id))
            await message.answer('Ваш новый аккаунт активирован! У вас есть бесплатный тестовый период на 3 дня. Нажмите ниже, чтобы подключиться и начать пользоваться сервисом', reply_markup=kb.install_app_step)
        except ZeroDivisionError:
            x = await get_link(message.chat.id)
            await message.answer(f'Вы успешно зарегистрированы') 
        except TypeError: pass

    @router.message(F.text == '🖥 Подключится')
    async def install_app(message: Message):
        link = await get_link(message.chat.id)
        x=f"""<b>Подключение к VPN происходит в 2 шага:</b>\n <blockquote>1. Кнопка "Скачать" - для загрузки приложения\n2. Кнопка "Подключить" - для добавления локаций</blockquote>\n\n🍏 iOS - iPhone, iPad и Mac\n📱 Устройства Android\n💻 Компьютеры Windows и Linux\n\n Ссылка для ручной установки \n<code>{link}</code>"""
        await message.answer(x, parse_mode='HTML', reply_markup=kb.install_app_kb)

    @router.message(F.text == 'ℹ️ Статус')
    async def profil(message: Message):
    
        await message.answer(f"До окончании подписки осталось: <blockquote>{await user_info(str(message.chat.id))}</blockquote>", parse_mode='HTML')
    @router.message(F.text == '🆘 Тех поддержка')
    async def sos(message: Message):
        await message.answer('🆘 Тех поддержка', reply_markup=kb.sos_kb(message.chat.id))

    @router.callback_query(F.data == 'install_app')
    async def install_app(callback_query: CallbackQuery):
        link = await get_link(callback_query.message.chat.id)
        x=f"""<b>Подключение к VPN происходит в 2 шага:</b>\n <blockquote>1. Кнопка "Скачать" - для загрузки приложения\n2. Кнопка "Подключить" - для добавления локаций</blockquote>\n\n🍏 iOS - iPhone, iPad и Mac\n📱 Устройства Android\n💻 Компьютеры Windows и Linux\n\n Ссылка для ручной установки \n<code>{link}</code>"""
        await callback_query.message.answer(x, parse_mode='HTML', reply_markup=kb.install_app_kb)

    @router.message(F.text == '💳 Оплатить доступ')
    async def buy_sub(message: Message):
        text = """
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
            f = ''
            try: await add_user(int(mons), str(callback_query.message.chat.id))
            except: f = await start_update(int(mons), callback_query.message.chat.id)#str(callback_query.message.from_user.id)) 
             
            await callback_query.message.edit_text(f'✅ Подписка продлена \n {f}')
        else: 
            await callback_query.message.answer(f'{x}')

   
@router.callback_query(F.data == 'tel_1')
async def tel_1(callback_query: CallbackQuery):
    x = await get_link(callback_query.message.chat.id)
    await callback_query.message.answer(f"""1.Нажмите на ссылку чтобы она скопировалась\n2.Откройте приложение и нажмите плюс в правой верхней части экрана \n<b>3.Выберите импорт из буфера обмена </b>
    <blockquote>Нажмите на ссылку для копирования</blockquote>""", reply_markup=kb.copy(x))
