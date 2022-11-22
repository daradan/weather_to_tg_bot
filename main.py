import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.inline_keyboard import InlineKeyboardButton

import geolocator as geo

API_TOKEN = '332274941:AAEOvYcE6Z7zW66HooQp7lg9NGVCMSgnf3c'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    markup = types.inline_keyboard.InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Add New Location/City', callback_data='add_location'))
    markup.add(InlineKeyboardButton('Change Settings', callback_data='settings'))
    markup.add(InlineKeyboardButton('Help', callback_data='help'))

    await message.answer('Hello', reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data == 'add_location')
async def process_callback_location(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Please, enter your location:')


@dp.message_handler()
async def custom_message(message: types.Message):
    user_location = message.text
    geolocation = geo.check_geolocator(user_location)
    msg = f"Is this your location:\n{geolocation['address']}"
    markup = types.inline_keyboard.InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Yes', callback_data='confirm_location'),
        InlineKeyboardButton('No', callback_data='add_location')
    )
    markup.add(InlineKeyboardButton('<< Back', callback_data='confirm_location'))
    await message.answer(msg, reply_markup=markup)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
