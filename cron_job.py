import asyncio
import datetime
from typing import List
from aiogram import Bot

from database import SessionLocal
import crud
from config import TG_TOKEN
import weather
from models import User, Settings, Location


bot = Bot(token=TG_TOKEN)


def get_formatted_time(for_notification=False):
    current_time = datetime.datetime.now()
    if for_notification:
        current_time += datetime.timedelta(minutes=1)
    cur_hour, cur_min = current_time.time().hour, current_time.time().minute
    hours = '0' * (cur_hour < 10) + str(cur_hour)
    mins = '0' * (cur_min < 10) + str(cur_min)
    return hours + ':' + mins


async def format_notifications(session, notifications: List[Settings]):
    body = []
    body_dict = {}
    for notification in notifications:
        body_dict['user_id'] = notification.user_id
        location: Location = crud.get_location_by_id(session=session, location_id=notification.location_id)
        body_dict['message'] = weather.get_weather(location, notification.language)
        body.append(body_dict)
    return body


async def send_messages(messages):
    for message in messages:
        await bot.send_message(chat_id=message['user_id'], text=message['message'], parse_mode='HTML')


def wait_until(notification_time):
    current_time = get_formatted_time()
    while notification_time > current_time:
        current_time = get_formatted_time()


async def start():
    session = SessionLocal()
    notification_time = get_formatted_time(for_notification=True)
    notifications: Settings = crud.get_settings_by_time(session=session, notification_time=notification_time)
    messages = await format_notifications(session, notifications)
    wait_until(notification_time)
    await send_messages(messages)
    session.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())
    loop.close()
