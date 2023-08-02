import sqlite3
import logging
import inspect
import telebot
import datetime
import itertools

from gspread.utils import rowcol_to_a1

import config
import keyboards


bot = telebot.TeleBot(config.TELEGRAM_TOKEN)


def is_new_user(user_username):
    """Checks if user already in database."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    users = cursor.execute(f'''SELECT COUNT(id) 
                            FROM users 
                            WHERE user_username=?
                            ''', (user_username,)).fetchall()[0][0]
    
    cursor.close()
    database.close()

    return users


def is_new_route(route_id):
    """Checks if user already in database."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    users = cursor.execute(f'''SELECT COUNT(id) 
                            FROM routes
                            WHERE unique_id=?
                            ''', (route_id,)).fetchall()[0][0]
    
    cursor.close()
    database.close()

    return users


def add_user(user_id, user_username):
    """Adds a new user to database."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''
        INSERT INTO users (user_id, user_username)
        VALUES (?, ?)
        ''', (user_id, user_username,))
        
    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Добавлен новый пользователь {user_username}.')


def add_user_id(user_id, user_username):
    '''Adds user_id to user's info.'''

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''UPDATE users
                    SET user_id=?
                    WHERE user_username=?
                    ''', (user_id, user_username,))

    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Добавлен id пользователя {user_username}.')


def add_allowed_user(user_username):
    '''Adds an allowed user to database.'''

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''
        INSERT INTO users (user_username, allowed)
        VALUES (?, ?)
        ''', (user_username, True,))
        
    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Добавлен новый разрешенный пользователь {user_username}.')


def allow_user(user_username):
    '''Makes user allowed.'''

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''UPDATE users
                    SET allowed=?
                    WHERE user_username=?
                    ''', (True, user_username,))

    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Пользователю {user_username} предоставлен доступ.')


def disallow_user(user_username):
    '''Makes user disallowed.'''

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''UPDATE users
                    SET allowed=?
                    WHERE user_username=?
                    ''', (False, user_username,))

    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Пользователь {user_username} лишен доступа.')


def check_if_allowed(user_id):
    '''Checks if user is allowed.'''

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    is_allowed = cursor.execute(f'''SELECT allowed 
                    FROM users 
                    WHERE user_id=?
                    ''', (user_id,)).fetchall()[0][0]
    
    cursor.close()
    database.close()

    return is_allowed


def get_user_id(user_username):
    '''Gets user's id by user's username.'''

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    user_id = cursor.execute(f'''SELECT user_id 
                    FROM users 
                    WHERE user_username=?
                    ''', (user_username,)).fetchall()
    
    cursor.close()
    database.close()

    if user_id:
        user_id = user_id[0][0]

    return user_id


def extract_all_users():
    """Extracts all users."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    users = cursor.execute("SELECT * FROM users").fetchall()

    cursor.close()
    database.close()

    return users


def clear_database():
    """Adds a new user to database."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute('DELETE FROM routes')
        
    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Таблица routes очищена.')


def construct_all_users_message(users):
    """Constructs message that contains information about all referrals."""

    replies = []
    count = 0
    reply_text = ''

    for num, user in enumerate(users):
        if user[3]:
            permission = 'допущен'
        else:
            permission = 'не допущен'

        reply_text += f'{num + 1}. @{user[2]} - {permission}\n'
        count += 1

        if count == 50 or count == len(users):
            replies.append(reply_text)
            reply_text = ''
            count = 0
    
    return replies


def get_bot_empty_row():
    '''Finds first empty row on a list.'''

    work_sheet = config.sheet.worksheet(config.LIST_BOT)
    return len(work_sheet.col_values(1)) + 1


def check_if_unique_id(list_name):
    '''Checks if all ids are unique.'''

    work_sheet = config.sheet.worksheet(list_name)
    ids = work_sheet.col_values(1)

    return len(ids) == len(set(ids))


def check_if_unique_username(list_name):
    '''Checks if all usernames are unique.'''

    work_sheet = config.sheet.worksheet(list_name)
    usernames = work_sheet.col_values(2)

    return len(usernames) == len(set(usernames))


def check_if_unique_name(list_name):
    '''Checks if all names are unique.'''

    work_sheet = config.sheet.worksheet(list_name)
    names = work_sheet.col_values(3)

    return len(names) == len(set(names))


def check_if_id_in_bot_list(id):
    work_sheet = config.sheet.worksheet(config.LIST_BOT)

    return id in work_sheet.col_values(1)


def validate_list(list_name):
    '''Validates list from which we need to extract data.'''
    try:
        work_sheet = config.sheet.worksheet(list_name)
    except:

        try:
            bot.send_message(chat_id=config.MANAGER_ID,
                         text=f'Лист с названием "{list_name}" не обнаружен.')
        except:
            pass

        return False
    
    if not check_if_unique_id(list_name):
        try:
            bot.send_message(chat_id=config.MANAGER_ID,
                         text='ID не уникальны. Исправьте ошибку и попробуйте снова.')
        except:
            pass
        
        return False
    
    elif not check_if_unique_username(list_name):
        try:
            bot.send_message(chat_id=config.MANAGER_ID,
                         text='Ники telegram не уникальны. Исправьте ошибку и попробуйте снова.')
        except:
            pass
        
        return False

    elif not check_if_unique_name(list_name):
        try:
            bot.send_message(chat_id=config.MANAGER_ID,
                         text='ФИО не уникальны. Исправьте ошибку и попробуйте снова.')
        except:
            pass
        
        return False
    
    return True


def add_route_to_database(info):
    '''Adds information about route.'''


    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''
        INSERT INTO routes (unique_id, user_username, user_id, addresses, phones, messages, route)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', info)
        
    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Добавлен новый маршрут {info[0]}.')


def add_route_to_spread(route_id, name, addresses):
    '''Adds information about route to spread.'''

    empty_row = get_bot_empty_row()

    work_sheet = config.sheet.worksheet(config.LIST_BOT)

    work_sheet.update(f'A{empty_row}:B{empty_row}', [[route_id, name]])

    col = 3
    for address in addresses:
        work_sheet.update_cell(empty_row, col, address)
        col += 6

    column = rowcol_to_a1(1, len(addresses) * 6 + 3).replace('1', '')

    work_sheet.format(f'{column}{empty_row}:EV{empty_row}', {"backgroundColor": {"red": 0.45, "green": 0.48, "blue": 0.48}})


def check_if_route(route):
    """Checks if route in database."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    routes = cursor.execute(f'''SELECT COUNT(id) 
                            FROM routes 
                            WHERE unique_id=?
                            ''', (route,)).fetchall()[0][0]
    
    cursor.close()
    database.close()

    return routes


def get_row_by_id(route_id):
    '''Gets row's number that contains route's id'''
    
    work_sheet = config.sheet.worksheet(config.LIST_BOT)

    try:
        row_num = work_sheet.col_values(1).index(route_id) + 1
    except:
        row_num = False

    return row_num


def color_cell_green(row_num):
    '''Colors id to green when driver starts the route.'''

    work_sheet = config.sheet.worksheet(config.LIST_BOT)

    work_sheet.format(f'A{row_num}', {"backgroundColor": {"red": 0.25, "green": 0.56, "blue": 0.0}})


def color_row_blue(row_num, point_num):

    work_sheet = config.sheet.worksheet(config.LIST_BOT)
    column = rowcol_to_a1(1, point_num * 6 + 2).replace('1', '')
    work_sheet.format(f'A{row_num}:{column}{row_num}', {"backgroundColor": {"red": 0.23, "green": 0.52, "blue": 0.75}})


def color_row_grey(row_num):

    work_sheet = config.sheet.worksheet(config.LIST_BOT)
    work_sheet.format(f'A{row_num}:EV{row_num}', {"backgroundColor": {"red": 0.45, "green": 0.48, "blue": 0.48}})


def color_row_yellow():

    work_sheet = config.sheet.worksheet(config.LIST_BOT)
    work_sheet.format(f'A1:EV1', {"backgroundColor": {"red": 0.84, "green": 0.68, "blue": 0.0}})


def get_address_phone(route_id):
    '''Gets address and phone of the point which is next to visit.'''

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    point_info = cursor.execute(f'''SELECT addresses, phones, messages 
                    FROM routes
                    WHERE unique_id=?
                    ''', (route_id,)).fetchall()[0]
    
    cursor.close()
    database.close()

    addresses = point_info[0].split('*&?#')
    phones = point_info[1].split('*&?#')
    info_messages = point_info[2].split('*&?#')

    point_info = tuple(zip(addresses, phones, info_messages))

    return point_info


def fill_arrive_time(row_num, current_status):
    work_sheet = config.sheet.worksheet(config.LIST_BOT)
    col_num = (current_status + 1) * 6 - 2
    current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime("%d.%m.%Y %H:%M")
    work_sheet.update_cell(row_num, col_num, current_time)


def fill_departure_time(row_num, current_status):
    work_sheet = config.sheet.worksheet(config.LIST_BOT)
    col_num = (current_status + 1) * 6 + 1
    current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime("%d.%m.%Y %H:%M")
    work_sheet.update_cell(row_num, col_num, current_time)


def fill_status(row_num, current_status, status):
    work_sheet = config.sheet.worksheet(config.LIST_BOT)
    col_num = (current_status + 1) * 6 - 1
    work_sheet.update_cell(row_num, col_num, status)


def fill_loader(row_num, current_status, status):
    work_sheet = config.sheet.worksheet(config.LIST_BOT)
    col_num = current_status * 6 + 2
    work_sheet.update_cell(row_num, col_num, status)


def fill_info_message(row_num, current_status, status):
    work_sheet = config.sheet.worksheet(config.LIST_BOT)
    col_num = current_status * 6
    work_sheet.update_cell(row_num, col_num, status)


def get_row_values(row_num, list_name):
    try:
        work_sheet = config.sheet.worksheet(list_name)
    except:

        try:
            bot.send_message(chat_id=config.MANAGER_ID,
                         text=f'Лист с названием "{list_name}" не обнаружен.')
        except:
            return False
    
    row_values = work_sheet.row_values(row_num)

    return row_values


def get_points_num_by_id(route_id):

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    points_num = cursor.execute(f'''SELECT route 
                    FROM routes
                    WHERE unique_id=?
                    ''', (route_id,)).fetchall()[0][0]

    return points_num


def update_database_status(route_id, status):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''UPDATE routes
                    SET status=?
                    WHERE unique_id=?
                    ''', (status, route_id,))

    database.commit()
    cursor.close()
    database.close()


def parse_data(list_name):
    # валидация данных на листе
    if validate_list(list_name):
        work_sheet = config.sheet.worksheet(list_name)
        routes = work_sheet.get_all_values()

        # валидация заголовков в таблице
        if validate_header(routes[0]):
            unfinished_routes = get_unfinished_routes()

            for route in unfinished_routes:
                row_num = get_row_by_id(route)
                if row_num:
                    color_row_grey(row_num)

            clear_database()
            

            handle_new_routes(routes[1::])

        else:
            try:
                bot.send_message(chat_id=config.MANAGER_ID,
                                    text=f'Неверные заголовки на листе "{list_name}".',
                                    )
            except:
                pass


def handle_new_routes(routes):
    # перебираем все маршруты
    for route in routes:
        # проверяем, что id маршрута ранее не использовался
        if not check_if_id_in_bot_list(route[0]):
            user_id = get_user_id(route[1])

            # проверяем id пользователя
            if user_id:
                
                # проверяем, что пользователю предоставлен доступ
                if check_if_allowed(user_id):
                    addresses = []
                    phones = []
                    info_messages = []
                    missed_address = -1

                    # перебираем адреса и номера телефонов в маршрутах
                    for num, element in enumerate(route[3::]):
                        if num % 3 == 0:
                            if element != '':
                                addresses.append(element)

                            else:
                                if route[3::][num + 1] == '' and route[3::][num + 2] == '':
                                    break
                                else:
                                    missed_address = int((num + 3) / 3)
                                    break

                        elif (num + 2) % 3 == 0:
                            phones.append(element)
                        
                        else:
                            info_messages.append(element)

                    # проверяем, что нет пропущенных адресов
                    if missed_address == -1:
                        points = len(addresses)

                        # проверяем, что количество адресов соответствует количеству номеров телефонов
                        if points == len(phones):
                            add_route_to_spread(route[0], route[2], addresses)
                            addresses = '*&?#'.join(addresses)
                            phones = '*&?#'.join(phones)
                            info_messages = '*&?#'.join(info_messages)
                            information = [route[0], route[1], user_id, addresses, phones, info_messages, points]
                            add_route_to_database(information)

                            try:
                                bot.send_message(chat_id=user_id,
                                                    text=f'У вас новый маршрут.\n*Количество адресов:* {points}',
                                                    reply_markup=keyboards.start_route_keyboard(route[0], points, 0),
                                                    parse_mode='Markdown',
                                                    )
                            except:

                                try:
                                    bot.send_message(chat_id=config.MANAGER_ID,
                                                        text=f'Не удалось оповестить {route[2]} о добавленном маршруте.',
                                                        )
                                except:
                                    pass
                        
                        else:
                            try:
                                bot.send_message(chat_id=config.MANAGER_ID,
                                                text=f'Идентификатор {route[0]} - неизвестная ошибка.',
                                                )
                            except:
                                pass

                    # пропущен адрес
                    else:
                        try:
                            bot.send_message(chat_id=config.MANAGER_ID,
                                            text=f'Идентификатор {route[0]}, пропущен адрес №{missed_address}.',
                                            )
                        except:
                            pass
                
                # нет доступа
                else:
                    try:
                        bot.send_message(chat_id=config.MANAGER_ID,
                                    text=f'Идентификатор маршрута: {route[0]}\nФИО: {route[2]}\nПользователю не предоставлен доступ.',
                                    )
                    except:
                        pass
            
            # бот не активирован
            else:
                try:
                    bot.send_message(chat_id=config.MANAGER_ID,
                                    text=f'Идентификатор маршрута: {route[0]}\nФИО: {route[2]}\nПользователь еще не активировал бота.',
                                    )
                except:
                    pass

        # идентификатор использовался ранее
        else:
            try:
                bot.send_message(chat_id=config.MANAGER_ID,
                                        text=f'Идентификатор {route[0]} уже добавлен в лист ответов бота.',
                                        )
            except:
                pass
    
    try:
        bot.send_message(chat_id=config.MANAGER_ID,
                         text='Команда обработана.')
    except:
        pass


def update_data(list_name):
    # валидация данных на листе
    if validate_list(list_name):
        work_sheet = config.sheet.worksheet(list_name)

        routes = work_sheet.get_all_values()

        # валидация заголовков в таблице
        if validate_header(routes[0]):

            new_routes = []

            # перебираем все маршруты
            for route in routes[1::]:
                if is_new_route(route[0]):

                    addresses = []
                    phones = []
                    info_messages = []
                    missed_address = -1

                    # перебираем адреса и номера телефонов в маршрутах
                    for num, element in enumerate(route[3::]):
                        if num % 3 == 0:
                            if element != '':
                                addresses.append(element)

                            else:
                                if route[3::][num + 1] == '' and route[3::][num + 2] == '':
                                    break
                                else:
                                    missed_address = int(num / 2 + 1)
                                    break

                        elif (num + 2) % 3 == 0:
                            phones.append(element)

                        else:
                            info_messages.append(element)

                    # проверяем, что нет пропущенных адресов
                    if missed_address == -1:
                        points = len(addresses)

                        # проверяем, что количество адресов соответствует количеству номеров телефонов
                        if points == len(phones):
                            route_info = get_route_info(route[0])

                            database_addresses = route_info[0].split('*&?#')

                            compare_addresses = tuple(zip(addresses, database_addresses))

                            first_difference = 100

                            for num, addresses_info in enumerate(compare_addresses):
                                if addresses_info[0] != addresses_info[1]: 
                                    first_difference = num
                                    break

                            if first_difference > route_info[1]:
                                update_route_in_spread(route[0], route[2], addresses)
                                update_database_route(route[0], addresses, phones, info_messages, points)

                                if points != route_info[2]:
                                    try:
                                        bot.send_message(chat_id=route_info[3],
                                                        text=f'Количество адресов в маршруте изменено.\nНовый маршрут из {points} адресов.',
                                                        )
                                    except:
                                        pass


                            else:
                                bot.send_message(chat_id=config.MANAGER_ID,
                                                text=f'Идентификатор {route[0]} - водитель уже получил информацию об адресе(-ах), куда внесены изменения.\nДля изменения маршрута водителя воспользуйтесь командой /stop {route[0]}',
                                                )

                        else:
                            try:
                                bot.send_message(chat_id=config.MANAGER_ID,
                                                text=f'Идентификатор {route[0]} - неизвестная ошибка.',
                                                )
                            except:
                                pass

                    # пропущен адрес
                    else:
                        try:
                            bot.send_message(chat_id=config.MANAGER_ID,
                                            text=f'Идентификатор {route[0]}, пропущен адрес №{missed_address}.',
                                            )
                        except:
                            pass
                
                # новые маршруты
                else:
                    new_routes.append(route)

            if new_routes:
                handle_new_routes(new_routes)
            
            else:
                try:
                    bot.send_message(chat_id=config.MANAGER_ID,
                                    text='Команда обработана.')
                except:
                    pass
        
        else:

            try:
                bot.send_message(chat_id=config.MANAGER_ID,
                                    text=f'Неверные заголовки на листе "{list_name}".',
                                    )
            except:
                pass


def get_route_info(route_id):

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    route_info = cursor.execute(f'''SELECT addresses, status, route, user_id
                            FROM routes 
                            WHERE unique_id=?
                            ''', (route_id,)).fetchall()[0]
    
    cursor.close()
    database.close()

    return route_info


def update_database_route(route_id, addresses, phones, info_messages, points_num):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    addresses = '*&?#'.join(addresses)
    phones = '*&?#'.join(phones)
    info_messages = '*&?#'.join(info_messages)

    cursor.execute(f'''UPDATE routes
                    SET addresses=?, phones=?, messages=?, route=?
                    WHERE unique_id=?
                    ''', (addresses, phones, info_messages, points_num, route_id,))

    database.commit()
    cursor.close()
    database.close()


def update_route_in_spread(route_id, name, addresses):
    '''Adds information about route to spread.'''

    row_num = get_row_by_id(route_id)

    if row_num:
        work_sheet = config.sheet.worksheet(config.LIST_BOT)

        work_sheet.update(f'A{row_num}:B{row_num}', [[route_id, name]])

        col = 3
        for address in addresses:
            work_sheet.update_cell(row_num, col, address)
            col += 6

        column = rowcol_to_a1(1, len(addresses) * 6 + 3).replace('1', '')

        work_sheet.format(f'A{row_num}:EV{row_num}', {"backgroundColor": {"red": 1, "green": 1, "blue": 1}})
        work_sheet.format(f'{column}{row_num}:EV{row_num}', {"backgroundColor": {"red": 0.45, "green": 0.48, "blue": 0.48}})


def delete_route(route_id):

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute('DELETE FROM routes WHERE unique_id=?', (route_id,))

    database.commit()
    cursor.close()
    database.close()


def get_unfinished_routes():

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    route_ids = cursor.execute(f'''SELECT unique_id
                            FROM routes 
                            WHERE finished=?
                            ''', (False,)).fetchall()
    
    cursor.close()
    database.close()

    if route_ids:
        route_ids = itertools.chain.from_iterable(route_ids)

    return route_ids


def set_finished(route_id):

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''UPDATE routes
                    SET finished=?
                    WHERE unique_id=?
                    ''', (True, route_id,))

    database.commit()
    cursor.close()
    database.close()


def validate_header(header):

    if 'id' not in header[0].lower():
        return False
    
    elif 'telegram' not in header[1].lower():
        return False
    
    elif 'фио' not in header[2].lower():
        return False
    
    elif 'сообщение' not in header[-1].lower():
        return False

    elif 'телефон' not in header[-2].lower():
        return False
    
    for col in header[3::3]:
        if 'адрес' not in col.lower():
            return False
            
    for col in header[4::3]:
        if 'телефон' not in col.lower():
                return False
    
    for col in header[5::3]:
        if 'сообщение' not in col.lower():
            return False

    return True


def update_header():
    work_sheet = config.sheet.worksheet(config.LIST_BOT)
    work_sheet.update('A1:EV1', [config.BOT_HEADER])