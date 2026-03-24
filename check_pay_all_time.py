import datetime
import time
import asyncio
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

# --- ФУНКЦИИ MARZBAN ---

async def add_user(mons, tgId):
    """Создание нового пользователя, если его нет (404)"""
    duration_days = 30 * int(mons)
    expiry_time = int(time.time() + duration_days * 24 * 60 * 60)
    api = MarzbanAPI(base_url=MARZBAN_URL)
    try:
        token = await api.get_token(username=ADMIN_USER, password=ADMIN_PASS)
        new_user = UserCreate(
            username=str(tgId),
            proxies={"vless": {"flow": "xtls-rprx-vision"}, "trojan": {}, "vmess": {}}, 
            data_limit=int(mons) * 200 * 1024**3, # 200ГБ за каждый месяц
            expire=expiry_time
        )
        await api.add_user(user=new_user, token=token.access_token)
        print(f"✅ Пользователь {tgId} создан на {mons} мес.")
    except Exception as e:
        print(f"❌ Ошибка создания {tgId}: {e}")

async def start_update(add_months, username, mod):
    """Продление существующего пользователя"""
    api = MarzbanAPI(base_url=MARZBAN_URL)
    add_months = int(add_months)
    try:
        token = await api.get_token(username=ADMIN_USER, password=ADMIN_PASS)
        user = await api.get_user(username=username, token=token.access_token)
        
        current_time = int(time.time())
        if mod == 0:
            seconds_to_add = add_months * 30 * 24 * 60 * 60
            base_time = user.expire if (user.expire and user.expire > current_time) else current_time
            new_expire = base_time + seconds_to_add
            # Прибавляем ГБ к текущему лимиту
            new_limit = (user.data_limit or 0) + (add_months * 200 * 1024**3)
        else: # Режим прямого указания timestamp
            new_expire = add_months
            new_limit = 1000 * 1024**3

        modify_data = UserModify(expire=new_expire, data_limit=new_limit, status="active")
        await api.modify_user(username=username, user=modify_data, token=token.access_token)
        print(f"🔄 {username} продлен до {time.ctime(new_expire)}")
    except Exception as e:
        print(f"❌ Ошибка продления {username}: {e}")

# --- ОСНОВНАЯ ЛОГИКА ---
async def sync_payments():
    # 1. Получаем платежи из ЮKassa за 20 дней
    print("⏳ Получение платежей из ЮKassa...")
    start_time = datetime.now(timezone.utc) - timedelta(days=360)
    
    try:
        res = Payment.list({"created_at.gte": start_time.isoformat(), "limit": 100})
        
        # Записываем в 1.txt: мес | дата | описание
        with open("1.txt", "w", encoding="utf-8") as f:
            if not res.items:
                print("ℹ️ Нет новых платежей.")
                return
            for p in res.items:
                if p.status == 'succeeded':
                    mons = int(float(p.amount.value) // 150)
                    if mons == 0: mons = 1 # Минимум 1 месяц если оплата < 150
                    f.write(f"{mons} | {p.created_at} | {p.description}\n")
        
        # 2. Обрабатываем файл и обновляем Marzban
        print("⏳ Обработка пользователей...")
        api = MarzbanAPI(base_url=MARZBAN_URL)
        token = await api.get_token(username=ADMIN_USER, password=ADMIN_PASS)

        with open("1.txt", "r", encoding="utf-8") as f:
            i = 0
            for line in f:
                i += 1
                parts = line.strip().split(" | ")
                if len(parts) < 3: continue
                
                mons_from_pay = int(parts[0])
                username = parts[2]

                try:
                    user = await api.get_user(username=username, token=token.access_token)
                    now = int(time.time())
                    user_expire = user.expire or 0
                    days_left = (user_expire - now) / (24 * 3600)

                    if days_left < 20:
                        await start_update(mons_from_pay, username, 0)
                    else:
                        print(f"{i} - ⏭️ {username} пропущен (осталось {int(days_left)} дн.)")
                
                except Exception as e:
                    if "404" in str(e):
                        await add_user(mons_from_pay, username)
                    else:
                        print(f"⚠️ Ошибка с {username}: {e}")

        print("🏁 Синхронизация завершена.")

    except Exception as e:
        print(f"🚨 Критическая ошибка: {e}")


