import time
import datetime
import timezonefinder, pytz
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types

import os
from dotenv import load_dotenv, find_dotenv
import certifi
import ssl
import geopy.geocoders
from geopy.geocoders import Nominatim
from database import SessionLocal
import crud

ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx

load_dotenv(find_dotenv())


class UserStates(StatesGroup):
    WELCOME = State()
    SET_LOCATION = State()
    SET_NOTIFICATION = State()
    NOTIFICATIONS_LIST = State()
    SELECT_NOTIFICATION = State()


def get_location(location_adr: str) -> dict:
    geolocator = Nominatim(user_agent=os.getenv('USER_AGENT'), scheme='http')
    location = geolocator.geocode(location_adr)
    tz, diff_time = get_difference_time(location.latitude, location.longitude)
    data = {
        'latitude': location.latitude,
        'longitude': location.longitude,
        'city': location.address,
        'timezone': tz,
        'diff_time': diff_time
    }
    return data


def get_difference_time(lat, lon):
    tf = timezonefinder.TimezoneFinder()
    timezone_str = tf.certain_timezone_at(lat=lat, lng=lon)
    timezone = pytz.timezone(timezone_str)
    dt_utc = datetime.datetime.utcnow()
    dt_now = datetime.datetime.now()
    dt_tz = dt_utc + timezone.utcoffset(dt_utc)
    diff_time = dt_now.hour - dt_tz.hour
    if dt_now < dt_tz:
        diff_time = dt_now.hour + dt_tz.hour
    return timezone_str, diff_time


def get_time(raw_time) -> tuple:
    if len(raw_time) != 4 and len(raw_time) != 5:
        return None, None
    time_formats = ['%H:%M', '%H %M', '%H-%M', '%H%M']
    for time_format in time_formats:
        try:
            t = time.strptime(raw_time, time_format)
            hours, mins = t.tm_hour, t.tm_min
            hours = '0' * (hours < 10) + str(hours)
            mins = '0' * (mins < 10) + str(mins)
            return hours, mins
        except ValueError:
            pass
    return None, None


def get_timeraw_create_settings(message: types.Message, city_raw, time_from_user):
    session = SessionLocal()
    geolocation = crud.get_or_add_location(session, city_raw)
    time_raw = f'{time_from_user[0]}:{time_from_user[1]}'
    hour = f'{int(time_from_user[0]) + int(geolocation.diff_time)}'
    if int(hour) >= 24:
        hour = f'{int(hour) - 24}'
    time_converted = "0" * (int(hour) < 10) + hour + f':{time_from_user[1]}'
    crud.create_settings(session, user_id=message.from_user.id, location_id=geolocation.id, notify_time_raw=time_raw,
                         notify_time=time_converted, language=message.from_user.language_code)
    session.close()
    return time_raw


def delete_notification(message: types.CallbackQuery) -> str:
    session = SessionLocal()
    notification_id = message.data.split('_')[-1]
    msg = 'Successfully deleted!'
    crud.delete_setting_by_id(session=session, notification_id=notification_id)
    session.close()
    return msg


if __name__ == '__main__':
    get_location('vancouver')
