import asyncio
import aiohttp
import datetime
import schedule
from datetime import date, timedelta
from check_schedule import check_schedule, check_schedule_to_all
from my_requests import add_user, get_all_users
from telebot.async_telebot import AsyncTeleBot
from telebot import util, types, asyncio_helper

TOKEN = "7122079884:AAHXd98FRmrHMf7mqHwysxza0Hs_6930yWE"

bot = AsyncTeleBot(TOKEN)

@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    text = "Привет \n\n<b>Полный список команд</b> \n\n/schedule - Прислать изменения в расписании."
    await bot.reply_to(message, text, parse_mode='HTML')
    add_user(message.from_user.id, message.from_user.first_name, message.from_user.username)

@bot.message_handler(commands=['schedule'])
async def send_welcome(message):
    await bot.reply_to(message, 'Проверяю расписание...')
    await check_schedule(message, 1)
    
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, 'Я могу работать только с командами \n Используй /help чтобы узнать список команд.')

async def send_photo(message):
    with open(f"img/{date.today()}.png", "rb") as photo:
        await bot.send_photo(message, photo)

async def send_legacy_schedule_photo(message):
    await bot.send_message(message, "Расписание на завтра еще не обновлено, скину расписание на сегодня.")
    with open(f"img/{date.today() - timedelta(days=1)}.png", "rb") as photo:
        await bot.send_photo(message, photo)

async def send_schedule_to_all(message):
    user_ids = get_all_users()
    for user_id in user_ids:
        try:
            with open(f"img/{date.today()}.png", "rb") as photo:
                await bot.send_photo(user_id, photo)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю с ID {user_id}: {e}")

async def async_schedule_job(coro):
    await coro

async def schedule_jobs():
    schedule.every(15).minutes.do(lambda: asyncio.create_task(check_schedule_to_all()))

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

async def main():
    print("Бот запущен... Ожидает команд.")

    await asyncio.gather(
        bot.polling(),
        schedule_jobs()
    )

if __name__ == "__main__":
    asyncio.run(main())

