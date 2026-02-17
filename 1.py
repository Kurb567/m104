import asyncio
from aiogram import Bot
import config as x

# Вставьте сюда токен вашего бота
BOT_TOKEN = "YOUR_BOT_TOKEN"
bot = Bot(token=x.TOKEN)

async def send_private_message(user_id: int, text: str):
    try:
        # Отправка сообщения
        await bot.send_message(chat_id=user_id, text=text)
        print(f"Сообщение успешно отправлено пользователю {user_id}")
    except Exception as e:
        # Ошибка, если пользователь заблокировал бота или ID неверен
        print(f"Не удалось отправить сообщение: {e}")
    finally:
        # Закрываем сессию бота
        await bot.session.close()

# Пример вызова:
if __name__ == "__main__":
    USER_ID = 7781754329  # ID получателя
   # MESSAGE = 'https://ctjkk.duckdns.org:8000/sub/NTg2MzkyNjYzNywxNzcxMjcyMzQ383HKSw8XYe'
    MESSAGE = "вот ваша ссылка скопируйте её и вставьте в приложение если возникнут проблемы напишите в тех поддержку"
    asyncio.run(send_private_message(USER_ID, MESSAGE))
