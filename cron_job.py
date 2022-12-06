import asyncio
import datetime

from aiogram import Bot

from database import SessionLocal
import crud
from config import TG_TOKEN

bot = Bot(token=TG_TOKEN)


def get_formatted_time(for_notification=False):
    current_time = datetime.datetime.now()
    if for_notification is True:
        current_time += datetime.timedelta(minutes=1)
    cur_hour, cur_min = current_time.time().hour, current_time.time().minute
    hours = '0' * (cur_hour < 10) + str(cur_hour)
    mins = '0' * (cur_min < 10) + str(cur_min)
    return hours + ':' + mins


def format_notifications(notifications):
    ...  # create messages for every notification
    body = {
        'user_id': 405161465,
        'message': 'test_notification'
    }
    return [body]


async def send_messages(messages):
    for message in messages:
        await bot.send_message(chat_id=message['user_id'], text=message['message'])  # send message to user


def wait_until(notification_time):
    current_time = get_formatted_time()
    while notification_time > current_time:
        current_time = get_formatted_time()


async def start():
    session = SessionLocal()
    notification_time = get_formatted_time(for_notification=True)
    notifications = crud.get_settings_by_time(session=session, notification_time=notification_time)
    messages = format_notifications(notifications)
    wait_until(notification_time)
    await send_messages(messages)
    session.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())
    loop.close()
