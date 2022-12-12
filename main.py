import logging
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext, filters
from aiogram.types.inline_keyboard import InlineKeyboardButton
from aiogram.contrib.fsm_storage.redis import RedisStorage2

import utils
from utils import UserStates
from config import TG_TOKEN
import keyboard_markup as kbm


bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot, storage=RedisStorage2())


@dp.message_handler(state='*', commands=['start', 'help'])
async def send_welcome(message: types.Message, state: FSMContext):
    await UserStates.WELCOME.set()
    markup = kbm.get_markup_welcome(message)
    await bot.send_message(message.from_user.id, f'Hello, <b>{message.from_user.first_name}</b>!',
                           reply_markup=markup, parse_mode='HTML')


@dp.callback_query_handler(lambda c: c.data == 'add_location', state=UserStates.WELCOME)
async def process_callback_add_location(message: types.CallbackQuery):
    await bot.send_message(message.from_user.id, 'Please, enter your location:')
    await UserStates.SET_LOCATION.set()


@dp.message_handler(state=UserStates.SET_LOCATION)
async def change_location(message: types.Message, state: FSMContext):
    try:
        markup, msg, geolocation = kbm.get_markup_location(message)
    except Exception as e:
        logging.exception(e)
        await message.answer(f'Location <b><u>{message.text}</u></b> not found.\nPlease, enter correct location!',
                             parse_mode='HTML')
        return
    await state.set_data({'city_raw': geolocation.city_raw})
    await message.answer(msg, reply_markup=markup, parse_mode='HTML')



@dp.callback_query_handler(lambda c: c.data == 'resend_location', state=UserStates.SET_LOCATION)
async def process_callback_add_location(message: types.CallbackQuery):
    await bot.send_message(message.from_user.id, 'Please, enter correct location!')


@dp.callback_query_handler(lambda c: c.data == 'confirm_location', state=UserStates.SET_LOCATION)
async def process_callback_confirm_location(message: types.CallbackQuery):
    await bot.send_message(message.from_user.id,
                           f'Please, enter notification time (HH MM / HH:MM / HH-MM / HHMM) 24 hour format')
    await UserStates.next()


@dp.message_handler(state=UserStates.SET_NOTIFICATION)
async def set_notification(message: types.Message, state: FSMContext):
    time_from_user = utils.get_time(message.text)
    if time_from_user[0] is None:
        await message.reply('Incorrect time format!', reply=False)
        return
    user_data = await state.get_data()
    time_raw = utils.get_timeraw_create_settings(message, user_data['city_raw'], time_from_user)
    await message.reply(f'Notification set to {time_raw}', reply=False)
    await send_welcome(message, state)


@dp.callback_query_handler(lambda c: c.data == 'list_notifications', state='*')
async def process_callback_list_notifications(message: types.CallbackQuery):
    markup = kbm.get_markup_notifications(message)
    await bot.send_message(message.from_user.id, 'Your Notifications:', reply_markup=markup)
    await UserStates.NOTIFICATIONS_LIST.set()


@dp.callback_query_handler(filters.Regexp(regexp=r'notification_\d+'), state=UserStates.NOTIFICATIONS_LIST)
async def process_callback_select_notification(message: types.CallbackQuery):
    markup, msg = kbm.get_markup_notification_settings(message)
    await UserStates.SELECT_NOTIFICATION.set()
    await bot.send_message(message.from_user.id, text=msg, reply_markup=markup, parse_mode='HTML')


@dp.callback_query_handler(filters.Regexp(regexp=r'delete_notification_\d+'), state=UserStates.SELECT_NOTIFICATION)
async def process_callback_delete_notification(message: types.CallbackQuery):
    msg = utils.delete_notification(message)
    await UserStates.NOTIFICATIONS_LIST.set()
    await bot.send_message(message.from_user.id, text=msg)
    await process_callback_list_notifications(message)


@dp.callback_query_handler(lambda c: c.data == 'back_to_menu', state='*')
async def process_callback_back_to_menu(message: types.Message, state: FSMContext):
    await send_welcome(message, state)


@dp.message_handler(state='*')
async def custom_message(message: types.Message, state: FSMContext):
    await send_welcome(message, state)


if __name__ == '__main__':
    logging.basicConfig(
        handlers=[RotatingFileHandler('weather_bot.log', mode='a+', maxBytes=10485760, backupCount=2, encoding='utf-8')],
        format="%(asctime)s %(levelname)s:%(message)s",
        level=logging.INFO,
    )
    executor.start_polling(dp, skip_updates=True)
