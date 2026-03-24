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
    """Создание нового пользователя"""
    expiry_time = int(time.time() + (int(mons) * 30 * 24 * 60 * 60))
    try:
        new_user = UserCreate(
            username=str(username),
            proxies={"vless": {"flow": "xtls-rprx-vision"}, "trojan": {}, "vmess": {}}, 
            data_limit=int(mons) * 200 * 1024**3,
            expire=expiry_time
        )
        await api.add_user(user=new_user, token=token.access_token)
        print(f"✅ Создан: {username} ({mons} мес.)")
    except Exception as e:
        print(f"❌ Ошибка создания {username}: {e}")

async def update_existing_user(api, token, user, mons):
    """Продление существующего пользователя"""
    current_time = int(time.time())
    add_seconds = int(mons) * 30 * 24 * 60 * 60
    
    # Считаем от даты истечения или от текущего момента (если просрочен)
    base_time = user.expire if (user.expire and user.expire > current_time) else current_time
    new_expire = base_time + add_seconds
    new_limit = (user.data_limit or 0) + (int(mons) * 200 * 1024**3)

    try:
        modify_data = UserModify(expire=new_expire, data_limit=new_limit, status="active")
        await api.modify_user(username=user.username, user=modify_data, token=token.access_token)
        print(f"🔄 Продлен: {user.username} до {time.ctime(new_expire)}")
    except Exception as e:
        print(f"❌ Ошибка продления {user.username}: {e}")

async def run_sync():
    api = MarzbanAPI(base_url=MARZBAN_URL)
    print(f"🚀 Запуск синхронизации за последний час: {datetime.now()}")

    try:
        # 1. Авторизация в Marzban
        token = await api.get_token(username=ADMIN_USER, password=ADMIN_PASS)

        # 2. Получение платежей из ЮKassa за 1 час
        start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        payments = Payment.list({"created_at.gte": start_time.isoformat(), "limit": 50})

        if not payments.items:
            print("💤 Новых успешных платежей нет.")
            return

        for p in payments.items:
            if p.status == 'succeeded' and p.description:
                username = p.description.strip()
                # Считаем месяцы: сумма / 150
                mons = int(float(p.amount.value) // 150)
                if mons == 0: mons = 1 

                try:
                    # 3. Проверка пользователя
                    user = await api.get_user(username=username, token=token.access_token)
                    
                    # Проверяем условие "осталось менее 20 дней"
                    now = int(time.time())
                    days_left = ((user.expire or 0) - now) / (24 * 3600)

                    if days_left < 20:
                        await update_existing_user(api, token, user, mons)
                    else:
                        print(f"⏭️ {username} пропущен (осталось {int(days_left)} дн.)")

                except Exception as e:
                    if "404" in str(e):
                        await add_new_user(api, token, username, mons)
                    else:
                        print(f"⚠️ Ошибка API для {username}: {e}")

    except Exception as e:
        print(f"🚨 Ошибка выполнения: {e}")

