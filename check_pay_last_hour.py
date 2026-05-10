import asyncio
import time
from datetime import datetime, timedelta, timezone
from yookassa import Payment
import yookassa
import config as x
from marzban import MarzbanAPI, UserModify, UserCreate

# --- НАСТРОЙКИ ---
yookassa.Configuration.configure(x.SHOP_ID, x.SECRET_KEY)
MARZBAN_URL = "https://ctjkk.duckdns.org:8000"
ADMIN_USER = "admin"
ADMIN_PASS = "56731096842"

async def add_new_user(api, token, username, mons):
    expiry_time = int(time.time() + (int(mons) * 30 * 24 * 60 * 60))
    try:
        new_user = UserCreate(
            username=str(username),
            proxies={"vless": {"flow": "xtls-rprx-vision"}, "trojan": {}, "vmess": {}}, 
            data_limit=int(mons) * 20 * 1024**3,
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
    new_limit = (user.data_limit or 0) + (int(mons) * 20 * 1024**3)
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
        
        
        for p in payments.items:
            if p.status == 'succeeded' and p.description: 
                username = p.description.strip()
                mons = int(float(p.amount.value) // 150)
                gb = 0
                if username[-7:] == "_add_gb":
                    gb = int(float(p.amount.value) // 3)
                    username = username[:-7]
                try:
                    user = await api.get_user(username=username, token=token.access_token)
                    file1 = open("pay_log.txt", "r")
                    if not p.id in file1.read():
                        if gb == 0:
                            await update_existing_user(api, token, user, mons)
                            with open("pay_log.txt", "a") as file:
                                file.write(p.id)
                                file.close()
                        else:
                            await add_gb_to_user(api, token, user, gb)
                            with open("pay_log.txt", "a") as file:
                                file.write(p.id)          
                                file.close()

                    
                except Exception as e:
                    if "404" in str(e):
                        await add_new_user(api, token, username, mons)
                    else:
                        print(f"⚠️ Ошибка API для {username}: {e}")

    except Exception as e: pass
        

