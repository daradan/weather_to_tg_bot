import logging
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext, filters
from aiogram.types.inline_keyboard import InlineKeyboardButton
from aiogram.contrib.fsm_storage.redis import RedisStorage2

import geolocator as geo
import utils
from database import SessionLocal
from utils import UserStates
from config import TG_TOKEN
import crud
from keyboard_markup import get_markup_welcome, get_markup_notifications, get_markup_notification_settings

# Configure logging
logging.basicConfig(
    # handlers=[RotatingFileHandler('bot.log', 'a+')],
    level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot, storage=RedisStorage2())


@dp.message_handler(state='*', commands=['start', 'help'])
async def send_welcome(message: types.Message, state: FSMContext):
    session = SessionLocal()
    await UserStates.WELCOME.set()
    cur_user = crud.get_or_create_user(session, user_obj=message.from_user)
    user_settings = crud.get_settings(session, user_id=cur_user.id)
    markup = get_markup_welcome(cur_user, user_settings)
    await bot.send_message(message.from_user.id, f'Hello, {message.from_user.first_name}', reply_markup=markup)
    session.close()


@dp.callback_query_handler(lambda c: c.data == 'add_location', state=UserStates.WELCOME)
async def process_callback_add_location(message: types.CallbackQuery):
    await bot.send_message(message.from_user.id, 'Please, enter your location:')
    await UserStates.SET_LOCATION.set()


@dp.callback_query_handler(lambda c: c.data == 'resend_location', state=UserStates.SET_LOCATION)
async def process_callback_add_location(message: types.CallbackQuery):
    await bot.send_message(message.from_user.id, 'Please, enter correct location')


@dp.callback_query_handler(lambda c: c.data == 'list_notifications', state='*')
async def process_callback_list_notifications(message: types.CallbackQuery):
    session = SessionLocal()
    notifications = crud.get_settings(session=session, user_id=message.from_user.id)
    markup = get_markup_notifications(notifications)
    await UserStates.NOTIFICATIONS_LIST.set()
    await bot.send_message(message.from_user.id, 'Your Notifications', reply_markup=markup)
    session.close()


@dp.callback_query_handler(lambda c: c.data == 'confirm_location', state=UserStates.SET_LOCATION)
async def process_callback_confirm_location(message: types.CallbackQuery):
    await bot.send_message(
        message.from_user.id,
        f'Please, enter notification time (HH MM / HH:MM / HH-MM / HHMM) 24 hour')
    await UserStates.next()


@dp.callback_query_handler(filters.Regexp(regexp=r'notification_\d+'), state=UserStates.NOTIFICATIONS_LIST)
async def process_callback_select_notification(message: types.CallbackQuery):
    session = SessionLocal()
    notification_id = message.data.split('_')[1]
    notification = crud.get_setting_by_id(session=session, notification_id=notification_id)
    text = f'Location: {notification.location}\nTime: {notification.notify_time}'
    markup = get_markup_notification_settings(notification_id)
    await UserStates.SELECT_NOTIFICATION.set()
    await bot.send_message(message.from_user.id, text=text, reply_markup=markup)
    session.close()


@dp.callback_query_handler(filters.Regexp(regexp=r'delete_notification_\d+'), state=UserStates.SELECT_NOTIFICATION)
async def process_callback_delete_notification(message: types.CallbackQuery):
    session = SessionLocal()
    notification_id = message.data.split('_')[-1]
    text = 'Successfully deleted!'
    crud.delete_setting_by_id(session=session, notification_id=notification_id)
    await UserStates.NOTIFICATIONS_LIST.set()
    await bot.send_message(message.from_user.id, text=text)
    await process_callback_list_notifications(message)
    session.close()


@dp.callback_query_handler(lambda c: c.data == 'back_to_menu', state='*')
async def process_callback_back_to_menu(message: types.Message, state: FSMContext):
    await send_welcome(message, state)


@dp.message_handler(state=UserStates.SET_LOCATION)
async def change_location(message: types.Message, state: FSMContext):
    user_location = message.text
    try:
        geolocation = geo.check_geolocator(user_location)
    except Exception as e:
        logging.exception(e)
        await message.answer(f'Location {user_location} not found')
        return
    msg = f"Is this your location:\n{geolocation['address']}"
    markup = types.inline_keyboard.InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Yes', callback_data='confirm_location'),
        InlineKeyboardButton('No', callback_data='resend_location')
    )
    markup.add(InlineKeyboardButton('<< Back', callback_data='back_to_menu'))
    await state.set_data({'location': geolocation['address']})
    await message.answer(msg, reply_markup=markup)


@dp.message_handler(state=UserStates.SET_NOTIFICATION)
async def set_notification(message: types.Message, state: FSMContext):
    session = SessionLocal()
    time_from_user = utils.get_time(message.text)
    if time_from_user[0] is None:
        await message.reply('Incorrect time format!', reply=False)
        return
    user_data = await state.get_data()
    time = f'{time_from_user[0]}:{time_from_user[1]}'
    location = user_data['location']
    crud.create_settings(session, user_id=message.from_user.id, location=location, notify_time=time)
    await message.reply(f'Notification set to {time_from_user[0]}:{time_from_user[1]}', reply=False)
    session.close()
    await send_welcome(message, state)


@dp.message_handler(state='*')
async def custom_message(message: types.Message, state: FSMContext):
    await send_welcome(message, state)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
