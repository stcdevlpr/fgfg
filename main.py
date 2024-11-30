import asyncio
import os
import random

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram import filters
from pyrogram.types import Message

# Загрузка переменных из .env
load_dotenv()

# Константы
DEFAULT_TIMEOUT_BETWEEN_MESSAGES = random.randint(60, 120)
DEFAULT_JOB_INTERVAL = random.randint(60, 120)
SESSION_NAME = "account"

# Настройки
custom_messages = [
    "Увидела Вашу заявку на канал. Меня зовут Юлия, я менеджер канала Льва Корнилова. \n\nЯ так понимаю, вам интересно сотрудничество по копитрейдингу или обучение криптовалютам, верно? 😊",
    "Приветствую! 👋\n Я Юлия, помощница Льва Викторовича. Увидела, что вы подписались на наш канал!\n\nПодскажите, вам более интересен копитрейдинг или обучение криптовалютам?",
    "Здравствуйте! 😊 Меня зовут Юлия, я помощница Льва Викторовича\n\nУвидела, что вы подписались на наш канал! Хотелось бы узнать, вам интересно больше узнать о копитрейдинге или о нашем обучении в криптовалютной сфере?",
    "Меня зовут Юлия, я помощница Льва Викторовича 👋🏻 \n\nУвидела, что вы подписались на наш канал. У вас есть интерес к возможности копитрейдинга или обучению в криптовалютной сфере?"
]


custom_interval = DEFAULT_JOB_INTERVAL
admin_id = int(os.getenv("Admin_id"))


# Получение переменных окружения
API_ID = str(os.getenv("Api_id"))
API_HASH = os.getenv("Api_hash")
PHONE_NUMBER = os.getenv("Phone_number")
CHANNEL_ID = str(os.getenv("Channel_id"))

# Создание клиента Pyrogram
client = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE_NUMBER,
)


# Планировщик
scheduler = AsyncIOScheduler()

# Функция для выбора случайного приветственного сообщения
def get_random_welcome_message():
    return random.choice(custom_messages)


async def check_client_status(channel_id):
    try:
        chat_member = await client.get_chat_member(channel_id, "me")
        return chat_member.status
    except Exception as e:
        print(f"Ошибка при проверке статуса: {e}")
        return None


async def approve_and_welcome_users():
    """
    Одобряет заявки на вступление в канал и отправляет приветственные сообщения.
    """
    status = await check_client_status(CHANNEL_ID)
    if status != ChatMemberStatus.ADMINISTRATOR:
        print("Клиент не является администратором канала. Завершение работы.")
        return

    try:
        async for request in client.get_chat_join_requests(CHANNEL_ID):
            user_id = request.user.id
            print(f"Одобряем заявку пользователя {user_id}")
            await client.approve_chat_join_request(CHANNEL_ID, user_id)

            try:
                welcome_message = get_random_welcome_message()
                print(f"Отправляем сообщение пользователю {user_id}")
                await client.send_message(user_id, welcome_message)
                await asyncio.sleep(DEFAULT_TIMEOUT_BETWEEN_MESSAGES)
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    except FloodWait as flood:
        print(f"Слишком много запросов. Ожидаем {flood.value} секунд.")
        await asyncio.sleep(flood.value)
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def start_scheduler(restart=False):
    """
    Запускает или перезапускает планировщик для выполнения задачи.
    """
    if restart:
        scheduler.remove_all_jobs()

    scheduler.add_job(approve_and_welcome_users, "interval", seconds=custom_interval)
    scheduler.start()
    print(f"Планировщик запущен с интервалом {custom_interval} секунд.")


async def main():
    """
    Основной процесс запуска клиента и планировщика.
    """
    print("Запуск клиента Pyrogram...")
    async with client:
        print("Клиент успешно авторизован.")
        start_scheduler()
        await asyncio.Event().wait()  # Ожидание завершения работы


@client.on_message(filters.private)
async def handle_private_message(message: Message):
    """
    Обработчик входящих сообщений.
    """
    print(f"Получено сообщение от {message.from_user.id}: {message.text}")
    await message.reply("Спасибо за ваше сообщение! Мы скоро ответим.")


if __name__ == "__main__":
    asyncio.run(main())  # Запуск asyncio.run только для основной функции
