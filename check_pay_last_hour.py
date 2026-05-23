import asyncio
import time
from datetime import datetime, timedelta, timezone
from yookassa import Payment
import yookassa
import os
import config as x
from marzban import MarzbanAPI, UserModify, UserCreate

# --- НАСТРОЙКИ ---
yookassa.Configuration.configure(x.SHOP_ID, x.SECRET_KEY)
MARZBAN_URL = "https://panel.567host.ru:8000"
ADMIN_USER = "admin"
ADMIN_PASS = "56731096842"

async def add_new_user(api, token, username, mons):
    expiry_time = int(time.time() + (int(mons) * 30 * 24 * 60 * 60))
    try:
        new_user = UserCreate(
            username=str(username),
            proxies={"vless": {"flow": "xtls-rprx-vision"}, "trojan": {}, "vmess": {}}, 
            data_limit=int(mons) * 200 * 1024**3,
            expire=expiry_time
        )
        await api.add_user(user=new_user, token=token.access_token)
        print(f"✅ Создан")
    except Exception as e: pass


async def update_existing_user(api, token, user, mons):
    """Продление существующего пользователя"""
    current_time = int(time.time())
    add_seconds = int(mons) * 30 * 24 * 60 * 60
    base_time = user.expire if (user.expire and user.expire > current_time) else current_time
    new_expire = base_time + add_seconds
    new_limit = (user.data_limit or 0) + (int(mons) * 200 * 1024**3)
    try:
        modify_data = UserModify(expire=new_expire, data_limit=new_limit, status="active")
        await api.modify_user(username=user.username, user=modify_data, token=token.access_token)
        print(f"🔄 Продлен: {user.username} до {time.ctime(new_expire)}")
    except Exception as e: pass 

async def add_gb_to_user(api, token, user, gb):
    new_limit = (user.data_limit or 0) + (gb * 1024**3)
    try:
        modify_data = UserModify(expire=user.expire, data_limit=new_limit, status="active")
        await api.modify_user(username=user.username, user=modify_data, token=token.access_token)
        print(f"🔄 Добавлено ГБ: {user.username} на {gb} ")
    except Exception as e: pass 

async def run_sync():
    api = MarzbanAPI(base_url=MARZBAN_URL)
    print(f"🚀 Запуск синхронизации за последний час: {datetime.now()}")
    try:
        token = await api.get_token(username=ADMIN_USER, password=ADMIN_PASS)
        start_time = datetime.now(timezone.utc) - timedelta(hours=1) # За последний час
        payments = Payment.list({"created_at.gte": start_time.isoformat(), "limit": 50})
        if not payments.items:
            print("💤 Новых успешных платежей нет.")
            return
        print(f"✅ Найдено {len(payments.items)} платежей за последний час.")
        
       

# Путь к файлу логов
        LOG_FILE = "pay_log.txt"

        # Предварительно создаем файл, если его нет, чтобы избежать ошибок чтения
        if not os.path.exists(LOG_FILE):
            open(LOG_FILE, "a").close()
        for p in payments.items:
            # 1. Исправлено: Добавлены кавычки для статуса
            if p.status == "succeeded" and p.description:
                # 2. Исправлено: Кавычки в f-строке
                print(f"🔍 Обработка платежа {p.id} для {p.description} на сумму {p.amount.value} {p.amount.currency}")
                
                username = p.description.strip()
                amount_float = float(p.amount.value)
                mons = int(amount_float // 150)
                gb = 0
                
                # 3. Исправлено: Кавычки для строки суффикса
                if username.endswith("_add_gb"):
                    gb = int(amount_float // 3) * 10 # 1 ГБ стоит 3 рубля, умножаем на 10 для получения количества ГБ
                    username = username[:-7]
                    
                try:
                    user = await api.get_user(username=username, token=token.access_token)
                    
                    # 4. Исправлено: Безопасное чтение файла через context manager
                    with open(LOG_FILE, "r") as file1:
                        log_content = file1.read().splitlines() # Читаем как список строк для точного совпадения ID
                        
                    if p.id not in log_content:
                        if gb == 0:
                            await update_existing_user(api, token, user, mons)
                        else:
                            await add_gb_to_user(api, token, user, gb)
                        with open(LOG_FILE, "a") as file:
                            file.write(f"{p.id}\n")
                            
                except Exception as e:
                    print(f"❌ Ошибка при обработке пользователя {username}: {e}")
            print(f"✅ Синхронизация завершена: {datetime.now()}")
    except Exception as e: pass
        

