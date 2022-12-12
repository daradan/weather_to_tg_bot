from aiogram import types
from aiogram.types import InlineKeyboardButton
import logging

from database import SessionLocal
import crud
from models import User, Settings, Location


def get_markup_welcome(message):
    session = SessionLocal()
    cur_user = crud.get_or_create_user(session, user_obj=message.from_user)
    user_settings = crud.get_settings(session, user_id=cur_user.id)
    markup = types.inline_keyboard.InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('New Notification', callback_data='add_location'))
    if cur_user and user_settings:
        markup.add(InlineKeyboardButton('My Notifications', callback_data='list_notifications'))
    markup.add(InlineKeyboardButton('Help', callback_data='help'))
    session.close()
    return markup


def get_markup_location(message: types.Message):
    session = SessionLocal()
    geolocation = crud.get_or_add_location(session, message.text)
    msg = f"Is this your location:\n<b>{geolocation.city}</b>"
    markup = types.inline_keyboard.InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Yes', callback_data='confirm_location'),
        InlineKeyboardButton('No', callback_data='resend_location')
    )
    markup.add(InlineKeyboardButton('<< Back', callback_data='back_to_menu'))
    session.close()
    return markup, msg, geolocation


def get_markup_notifications(message: types.CallbackQuery):
    markup = types.inline_keyboard.InlineKeyboardMarkup()
    session = SessionLocal()
    count = 0
    settings_dict = {}
    locations = []
    settings = crud.get_settings(session=session, user_id=message.from_user.id)
    for setting in settings:
        locations.append(crud.get_location_by_id(session=session, location_id=setting.location_id))
    for location in locations:
        for notify_time in settings:
            settings_dict[location.city] = notify_time.notify_time_raw
    for location, notify_time in settings_dict.items():
        text = f"{notify_time} | {location}"
        btn = InlineKeyboardButton(text=text, callback_data=f'notification_{settings[count].id}')
        count += 1
        markup.add(btn)
    markup.add(InlineKeyboardButton(text='<< Back', callback_data='back_to_menu'))
    session.close()
    return markup


def get_markup_notification_settings(message: types.CallbackQuery):
    session = SessionLocal()
    markup = types.inline_keyboard.InlineKeyboardMarkup()
    notification_id = message.data.split('_')[1]
    notification: Settings = crud.get_setting_by_id(session=session, notification_id=notification_id)
    location: Location = crud.get_location_by_id(session=session, location_id=notification.location_id)
    msg = f'<b>Location:</b> {location.city}\n<b>Time:</b> {notification.notify_time_raw}'
    markup.add(InlineKeyboardButton('Delete', callback_data=f'delete_notification_{notification_id}'))
    markup.add(InlineKeyboardButton('<< Back', callback_data='list_notifications'))
    session.close()
    return markup, msg
