from telebot import types

import config

def start_route_keyboard(route, points, status):
    """Generates main keyboard that have option of filling form, check instagram."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Начать', callback_data = f'start_{route}_{points}_{status}'))

    return keyboard


def connect_admin_keyboard():
    """Connect to administrator button."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Администратор', url = f'https://t.me/{config.MANAGER_USERNAME}'))

    return keyboard


def arrived_keyboard(route, points, status):
    '''Arrived button.'''

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Прибыл', callback_data = f'arrived_{route}_{points}_{status}'))

    return keyboard


def departed_keyboard(route, points, status):
    '''Arrived button.'''

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Убыл', callback_data = f'departed_{route}_{points}_{status}'))

    return keyboard


def finish_route_keyboard(route, points, status):
    """Generates main keyboard that have option of filling form, check instagram."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Завершить маршрут', callback_data = f'finish_{route}_{points}_{status}'))

    return keyboard


def amount_keyboard(route, points, status):

    keyboard = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton('Да', callback_data = f'amount_{route}_{points}_{status}_yes')
    no = types.InlineKeyboardButton('Нет', callback_data = f'amount_{route}_{points}_{status}_no')
    keyboard.add(yes, no)

    return keyboard


def loader_keyboard(route, points, status):

    keyboard = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton('Да', callback_data = f'loader_{route}_{points}_{status}_yes')
    no = types.InlineKeyboardButton('Нет', callback_data = f'loader_{route}_{points}_{status}_no')
    keyboard.add(yes, no)

    return keyboard

def info_keyboard():

    return types.ForceReply(input_field_placeholder='Информация')