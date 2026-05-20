from aiogram import types, F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from yookassa import Configuration, Payment
from marzban import MarzbanAPI, UserCreate
from marzban.models import UserModify
from check_pay_last_hour import *
import app.keyboard as kb
import config as x
import json 
import random 
import time
import uuid
import datetime


router = Router()
Configuration.configure(x.SHOP_ID, x.SECRET_KEY)
async def get_link(tgId):
    api = MarzbanAPI(base_url="https://ctjkk.duckdns.org:8000")
    token = await api.get_token(username="admin", password="56731096842")
    user = await api.get_user(username=tgId, token=token.access_token)
    return user.subscription_ur

async def copy_user(source_username: str, target_username: str):
    api = MarzbanAPI(base_url="https://duckdns.org")

    try:
        token_data = await api.get_token(
            username="admin", password="56731096842"
        )
        token = token_data.access_token
    except Exception as e:
        print(f"Ошибка авторизации в Marzban API: {e}")
        return False

    try:
        source_user = await api.get_user(username=source_username, token=token)
        if not source_user:
            print(f"Пользователь-донор {source_username} не найден.")
            return False

        source_traffic = source_user.data_limit
        source_expire = source_user.expire

        target_user = await api.get_user(username=target_username, token=token)
        if not target_user:
            print(f"Пользователь-получатель {target_username} не найден.")
            return False

        updated_data = UserModify(
            proxies=target_user.proxies,
            status=target_user.status,
            on_demand=target_user.on_demand,
            data_limit=source_traffic,
            expire=source_expire,
        )

        await api.modify_user(
            username=target_username, user=updated_data, token=token
        )

        print(
            f"Успешно скопировано! Трафик и время пользователя {source_username} перенесены для {target_username}."
        )
        return True

    except Exception as e:
        print(f"Произошла ошибка при копировании: {e}")
        return False


async def add_user(mons, tgId):
    duration_days = 3
    duration_days *= int(mons)
    expiryTime = int((time.time() + duration_days * 24 * 60 * 60))
    api = MarzbanAPI(base_url="https://ctjkk.duckdns.org:8000/")
    token = await api.get_token(username="admin", password="56731096842")

    new_user = UserCreate(
        username=str(tgId),
        proxies={"vless": { "flow": "xtls-rprx-vision" }, "trojan":{}, "vmess":{}}, 
        data_limit=200*1024*1024*1024, # 200 ГБ в байтах
        expire=expiryTime)
    try:
        user = await api.add_user(user=new_user, token=token.access_token)
        print(f"Пользователь создан!")
    except Exception as e:
        return 10/0

async def user_info(tgId: str):
    api = MarzbanAPI(base_url="https://ctjkk.duckdns.org:8000")
    try:
        token = await api.get_token(username="admin", password="56731096842")
        user = await api.get_user(username=tgId, token=token.access_token)
        if not user.expire:
            return "Безлимитно"
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
        x = await get_link(message.chat.id)
        await message.answer(f"До окончании подписки осталось: <blockquote>{await user_info(str(message.chat.id))}</blockquote>", parse_mode='HTML', reply_markup=kb.status_kb(x))

    @router.message(F.text == '🆘 Тех поддержка')
    async def sos(message: Message):
        await message.answer('🆘 Тех поддержка', reply_markup=kb.sos_kb(message.chat.id))

    @router.message(F.text == '/a')
    async def a_link(message: Message):
        await add_user(1, f'{message.chat.id}a')
        await copy_user(message.chat.id, f'{message.chat.id}a')  

    @router.message(F.text == '/b')
    async def b_link(message: Message):
        await add_user(1, f'{message.chat.id}b')
        await copy_user(message.chat.id, f'{message.chat.id}b')  

    @router.message(F.text == '/a_get_link')    
    async def a_get_link(message: Message):
        link = await get_link(f'{message.chat.id}a')
        await message.answer(f'Ссылка для пользователя {message.chat.id}a: {link}')

    @router.message(F.text == '/b_get_link')    
    async def b_get_link(message: Message):
        link = await get_link(f'{message.chat.id}b')
        await message.answer(f'Ссылка для пользователя {message.chat.id}b: {link}')

    @router.callback_query(F.data == 'devices')
    async def devices(callback_query: CallbackQuery):
        await callback_query.message.answer("Можно подключить до трех устройств введите /a для первого и /b для второго. После этого вы сможете получить ссылки для каждого устройства по командам /a_get_link и /b_get_link соответственно. Введите /a и /b еще раз для обновления ссылок, если вы оплатили продление подписки или докупили трафик")    

    @router.callback_query(F.data == 'sos_kb_1')
    async def sos(callback_query: CallbackQuery):
        await callback_query.message.answer('🆘 Тех поддержка', reply_markup=kb.sos_kb(callback_query.message.chat.id))    

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

class Paymen1t:
    @router.callback_query(F.data.startswith('buy_sub_'))
    async def buy_sub_(callback_query: CallbackQuery):
        mons = callback_query.data[-1]
        if mons == '2':
            mons = '12'
        rub = f'{int(mons)*150}.00'  
        url, payment_id = create_payment(rub, str(callback_query.message.chat.id), "https://t.me/HappPlus_bot")
        text = f"""💳 Оформление продления \n\n⏱️ Срок: {int(mons)*30} дней\n💰 Стоимость: {int(mons)*150} RUB\n\nНажмите кнопку «💳 Оплатить» ниже, чтобы перейти к оплате.\n\nID операции: <code>{payment_id}</code>"""
        await callback_query.message.answer(text, reply_markup=kb.check_pay(url, payment_id, mons))
        for i in range(15):
            await asyncio.sleep(60)
            await run_sync()

    @router.callback_query(F.data[-1] == 'b')
    async def buy_sub_(callback_query: CallbackQuery):
        if callback_query.data == 'buy_200_gb': rub = '60.00'
        elif callback_query.data == 'buy_500_gb': rub = '150.00'
        elif callback_query.data == 'buy_1000_gb': rub = '300.00'
        url, payment_id = create_payment(rub, f"{callback_query.message.chat.id}_add_gb", "https://t.me/HappPlus_bot")
        text = f"💳 Докупка трафика \n\n Трафик: {float(rub)/3} ГБ\n💰 Стоимость: {rub} RUB\n\nНажмите кнопку «💳 Оплатить» ниже, чтобы перейти к оплате.\n\nID операции: <code>{payment_id}</code>"
        await callback_query.message.answer(text, reply_markup=kb.check_pay(url, payment_id, '1'))
        for i in range(15):
            await run_sync()
            await asyncio.sleep(60)
            

@router.callback_query(F.data == 'tel_1')
async def tel_1(callback_query: CallbackQuery):
    x = await get_link(callback_query.message.chat.id)
    await callback_query.message.answer(f"""1.Нажмите на ссылку чтобы она скопировалась\n2.Откройте приложение и нажмите <b>ПЛЮС</b> в правой верхней части экрана \n<b>3.Выберите импорт из буфера обмена </b>
    <blockquote>Нажмите на ссылку для копирования</blockquote>""", reply_markup=kb.copy(x))
    