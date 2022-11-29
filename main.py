import logging
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.types.inline_keyboard import InlineKeyboardButton
from aiogram.contrib.fsm_storage.redis import RedisStorage2

import geolocator as geo
import utils
from database import SessionLocal
from utils import UserStates
from config import TG_TOKEN
from crud import get_user, create_user

# Configure logging
logging.basicConfig(
    # handlers=[RotatingFileHandler('bot.log', 'a+')],
    level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot, storage=RedisStorage2())


@dp.message_handler(state='*', commands=['start', 'help'])
async def send_welcome(message: types.Message):
    session = SessionLocal()
    await UserStates.WELCOME.set()
    cur_user = get_user(session, message.from_user.id)
    if not cur_user:
        cur_user = create_user(session, message.from_user)
    markup = types.inline_keyboard.InlineKeyboardMarkup()
    if not cur_user or not cur_user.location:
        markup.add(InlineKeyboardButton('Add New Location/City', callback_data='add_location'))
        markup.add(InlineKeyboardButton('Help', callback_data='help'))
    else:
        markup.add(InlineKeyboardButton('Change Location', callback_data='add_location'))
        markup.add(InlineKeyboardButton('Change Settings', callback_data='change_settings'))
        markup.add(InlineKeyboardButton('Help', callback_data='help'))
    await bot.send_message(message.from_user.id, f'Hello, {message.from_user.first_name}', reply_markup=markup)
    session.close()


@dp.callback_query_handler(lambda c: c.data == 'add_location', state=UserStates.WELCOME)
async def process_callback_add_location(message: types.Message):
    await bot.send_message(message.from_user.id, 'Please, enter your location:')
    await UserStates.SET_LOCATION.set()


@dp.callback_query_handler(lambda c: c.data == 'resend_location', state=UserStates.SET_LOCATION)
async def process_callback_add_location(message: types.Message):
    await bot.send_message(message.from_user.id, 'Please, enter correct location')


@dp.callback_query_handler(lambda c: c.data == 'confirm_location', state=UserStates.SET_LOCATION)
async def process_callback_confirm_location(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        f'Location has been saved!\n'
        f'Please, enter notification time (HH MM / HH:MM / HH-MM / HHMM) 24 hour')
    await UserStates.next()


@dp.callback_query_handler(lambda c: c.data == 'back_to_menu', state='*')
async def process_callback_back_to_menu(message: types.Message):
    await send_welcome(message)


@dp.message_handler(state=UserStates.SET_LOCATION)
async def change_location(message: types.Message):
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
    markup.add(InlineKeyboardButton('<< Back to menu', callback_data='back_to_menu'))
    await message.answer(msg, reply_markup=markup)


@dp.message_handler(state=UserStates.SET_NOTIFICATION)
async def change_location(message: types.Message):
    time_from_user = utils.get_time(message.text)
    if time_from_user[0] is None:
        await message.reply('Incorrect time format!', reply=False)
        return
    await message.reply(f'Notification set to {time_from_user[0]}:{time_from_user[1]}', reply=False)
    await UserStates.WELCOME.set()


@dp.message_handler(state='*')
async def custom_message(message: types.Message):
    await send_welcome(message)


# @dp.message_handler(state='*')
# async def custom_message(message: types.Message):
#     user_location = message.text
#     geolocation = geo.check_geolocator(user_location)
#     msg = f"Is this your location:\n{geolocation['address']}"
#     markup = types.inline_keyboard.InlineKeyboardMarkup()
#     markup.add(
#         InlineKeyboardButton('Yes', callback_data='confirm_location'),
#         InlineKeyboardButton('No', callback_data='add_location')
#     )
#     markup.add(InlineKeyboardButton('<< Back', callback_data='confirm_location'))
#     await message.answer(msg, reply_markup=markup)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
