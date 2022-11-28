from aiogram.dispatcher.filters.state import State, StatesGroup


class UserStates(StatesGroup):
    WELCOME = State()
    SET_LOCATION = State()
    SET_NOTIFICATION = State()
    CHANGE_LOCATION = State()
    CHANGE_SETTINGS = State()
