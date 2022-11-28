import logging
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.types.inline_keyboard import InlineKeyboardButton
# from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import geolocator as geo
from utils import UserStates
from config import TG_TOKEN

# Configure logging
logging.basicConfig(
    # handlers=[RotatingFileHandler('bot.log', 'a+')],
    level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(state='*', commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await UserStates.WELCOME.set()
    markup = types.inline_keyboard.InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Add New Location/City', callback_data='add_location'))
    markup.add(InlineKeyboardButton('Help', callback_data='help'))

    await message.answer('Hello', reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data == 'add_location', state='*')
async def process_callback_location(message: types.Message):
    await bot.send_message(message.from_user.id, 'Please, enter your location:')
    await UserStates.SET_LOCATION.set()


@dp.message_handler(state=UserStates.SET_LOCATION)
async def change_location(message: types.Message):
    # get location and set it
    await message.reply(f'Location {message.text} has been saved!\nPlease, enter notification time:', reply=False)
    await UserStates.next()


@dp.message_handler(state=UserStates.SET_NOTIFICATION)
async def change_location(message: types.Message):
    # save notification preferences
    await message.reply('Notification Preferences have been saved!', reply=False)
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
