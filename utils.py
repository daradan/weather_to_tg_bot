import time
from aiogram.dispatcher.filters.state import State, StatesGroup


class UserStates(StatesGroup):
    WELCOME = State()
    SET_LOCATION = State()
    SET_NOTIFICATION = State()
    CHANGE_LOCATION = State()
    CHANGE_SETTINGS = State()


def get_time(raw_time):
    if len(raw_time) != 4 and len(raw_time) != 5:
        return None, None
    time_formats = ['%H:%M', '%H %M', '%H-%M', '%H%M']
    for time_format in time_formats:
        try:
            t = time.strptime(raw_time, time_format)
            return t.tm_hour, t.tm_min
        except ValueError:
            pass
    return None, None
