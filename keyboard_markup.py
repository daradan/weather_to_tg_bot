from typing import List

from aiogram import types
from aiogram.types import InlineKeyboardButton

from models import Settings


def get_markup_welcome(user, settings):
    markup = types.inline_keyboard.InlineKeyboardMarkup()
    if not user or not settings:
        markup.add(InlineKeyboardButton('New Notification', callback_data='add_location'))
        markup.add(InlineKeyboardButton('Help', callback_data='help'))
    else:
        markup.add(InlineKeyboardButton('New Notification', callback_data='add_location'))
        markup.add(InlineKeyboardButton('My Notifications', callback_data='list_notifications'))
        markup.add(InlineKeyboardButton('Help', callback_data='help'))
    return markup


def get_markup_notifications(notification_list: List[Settings]):
    markup = types.inline_keyboard.InlineKeyboardMarkup()
    for notification in notification_list:
        text = f'{notification.location} | {notification.notify_time}'
        btn = InlineKeyboardButton(text=text, callback_data=f'notification_{notification.id}')
        markup.add(btn)
    return markup
