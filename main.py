import telebot
import logging
import threading
import os
import inspect

import config
import utils
import functions
import keyboards


logging.basicConfig(level=logging.ERROR, 
                    filename="py_log.log", 
                    filemode="w", 
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    )

bot = telebot.TeleBot(config.TELEGRAM_TOKEN)

functions.update_header()
functions.color_row_yellow()

@bot.message_handler(commands=['start'])
def start_message(message):
    '''Handles start command.'''

    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    user_username = message.from_user.username

    if user_username is not None:

        if user_id == config.MANAGER_ID:
            bot.send_message(chat_id=chat_id,
                         text=config.HELP_MESSAGE,
                         parse_mode='Markdown',
                         )

        else:
            if functions.is_new_user(user_username):
                functions.add_user_id(user_id, user_username)
            else:
                functions.add_user(user_id, user_username)

            if functions.check_if_allowed(user_id):
                bot.send_message(chat_id=chat_id,
                         text=config.ALLOWED_MESSAGE,
                         )
            else:
                bot.send_message(chat_id=chat_id,
                         text=config.NOT_ALLOWED_MESSAGE,
                         )
                
    else:
        bot.send_message(chat_id=chat_id,
                         text=config.NO_USERNAME_MESSAGE,
                         )
        

@bot.message_handler(commands=['allow'])
def add_allowed_user_command(message):
    if str(message.from_user.id) == config.MANAGER_ID:
        user_username = message.text.split(' ')[-1].strip('@')

        if functions.is_new_user(user_username):
            functions.allow_user(user_username)
            user_id = functions.get_user_id(user_username)

            try:
                bot.send_message(chat_id=user_id,
                                 text=config.ALLOWED_MESSAGE,
                                 )
            except:
                pass

            bot.send_message(chat_id=message.chat.id,
                             text=f'Пользователь @{user_username} добавлен в список допущенных и оповещен.',
                             )

        else:
            functions.add_allowed_user(user_username)

            bot.send_message(chat_id=message.chat.id,
                             text=f'Пользователь @{user_username} добавлен в список допущенных, но еще не взаимодействовал с ботом.',
                             )

    else:
        bot.send_message(chat_id=message.chat.id,
                         text=config.NO_PERMISSIONS_MESSAGE,
                         )


@bot.message_handler(commands=['disallow'])
def add_allowed_user_command(message):
    if str(message.from_user.id) == config.MANAGER_ID:
        user_username = message.text.split(' ')[-1].strip('@')

        if functions.is_new_user(user_username):
            functions.disallow_user(user_username)
            user_id = functions.get_user_id(user_username)

            try:
                bot.send_message(chat_id=user_id,
                                 text=config.DISALLOWED_MESSAGE,
                                 )
            except:
                pass
            
            bot.send_message(chat_id=message.chat.id,
                             text=f'Пользователь @{user_username} исключен из списка допущенных.',
                             )

        else:
            bot.send_message(chat_id=message.chat.id,
                             text=f'Пользователя с ником @{user_username} нет в базе данных.',
                             )
    else:
        bot.send_message(chat_id=message.chat.id,
                         text=config.NO_PERMISSIONS_MESSAGE,
                         )


@bot.message_handler(commands=['all_users'])
def add_allowed_user_command(message):
    if str(message.from_user.id) == config.MANAGER_ID:
        all_users = functions.extract_all_users()
        replies = functions.construct_all_users_message(all_users)

        for reply in replies:
            try:
                bot.send_message(chat_id=message.chat.id,
                                 text=reply,
                                 )
            except:
                logging.error(f'{inspect.currentframe().f_code.co_name}: Не удалось отправить сообщение по команде all_users.')

    else:
        bot.send_message(chat_id=message.chat.id,
                         text=config.NO_PERMISSIONS_MESSAGE,
                         )


@bot.message_handler(commands=['send_routes'])
def add_allowed_user_command(message):
    if str(message.from_user.id) == config.MANAGER_ID:
        list_name = message.text.replace('/send_routes ', '')

        functions.parse_data(list_name)

    else:
        bot.send_message(chat_id=message.chat.id,
                         text=config.NO_PERMISSIONS_MESSAGE,
                         )


@bot.message_handler(commands=['update_routes'])
def add_allowed_user_command(message):
    if str(message.from_user.id) == config.MANAGER_ID:
        list_name = message.text.replace('/update_routes ', '')

        functions.update_data(list_name)

    else:
        bot.send_message(chat_id=message.chat.id,
                         text=config.NO_PERMISSIONS_MESSAGE,
                         )


@bot.message_handler(commands=['stop'])
def add_allowed_user_command(message):
    if str(message.from_user.id) == config.MANAGER_ID:
        route_id = message.text.replace('/stop ', '')

        if functions.is_new_route(route_id):
            user_id = functions.get_route_info(route_id)[3]
            functions.delete_route(route_id)
            row_num = functions.get_row_by_id(route_id)

            if row_num:
                functions.color_row_grey(row_num)
            
            try:
                bot.send_message(chat_id=user_id,
                                 text='Ваш маршрут отменен. Ожидайте новой информации.',
                                 )
            except:
                pass

            try:
                bot.send_message(chat_id=config.MANAGER_ID,
                                 text=f'Маршрут {route_id} отменен.',
                                 )
            except:
                pass

        else:
            bot.send_message(chat_id=message.chat.id,
                        text=f'Идентификатор {route_id} не найден.',
                        )

    else:
        bot.send_message(chat_id=message.chat.id,
                         text=config.NO_PERMISSIONS_MESSAGE,
                         )


@bot.message_handler(commands=['connect'])
def add_allowed_user_command(message):
    bot.send_message(chat_id=message.chat.id,
                     text='Нажмите для связи с администратором:',
                     reply_markup=keyboards.connect_admin_keyboard(),
                     )


@bot.message_handler(commands=['help'])
def add_allowed_user_command(message):
    if str(message.from_user.id) == config.MANAGER_ID:
        bot.send_message(chat_id=message.chat.id,
                        text=config.HELP_MESSAGE,
                        )
    else:
        bot.send_message(chat_id=message.chat.id,
                         text=config.NO_PERMISSIONS_MESSAGE,
                         )


@bot.callback_query_handler(func = lambda call: True)
def callback_query(call):
    """Handles queries from inline keyboards."""

    # getting message's and user's ids
    message_id = call.message.id
    chat_id=call.message.chat.id

    call_data = call.data.split('_')
    query = call_data[0]
    route_id = call_data[1]

    if functions.check_if_route(route_id):
        row_num = functions.get_row_by_id(route_id)

        if row_num:
            points_num = functions.get_points_num_by_id(route_id)
            current_status = int(call_data[3])

            if query == 'start':
                functions.color_cell_green(row_num)
                point_data = functions.get_address_phone(route_id)[current_status]

                address = point_data[0]
                phone = point_data[1]
                info_message = point_data[2]

                if info_message == '':
                    info_message = '-'

                bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=f'АДРЕС: {address}\nТелефон: {phone}\nСообщение от логиста: {info_message}',
                                    )
                
                bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=keyboards.arrived_keyboard(route_id, points_num, current_status),
                                            )
        
            elif query == 'arrived':
                functions.fill_arrive_time(row_num, current_status)
                functions.fill_status(row_num, current_status, 'прибыл')

                if current_status + 1 == points_num:
                    bot.edit_message_reply_markup(chat_id=chat_id,
                                                  message_id=message_id,
                                                  reply_markup=keyboards.finish_route_keyboard(route_id, points_num, current_status),
                                                  )
                else:
                    bot.edit_message_reply_markup(chat_id=chat_id,
                                                  message_id=message_id,
                                                  reply_markup=keyboards.departed_keyboard(route_id, points_num, current_status),
                                                  )
            
            elif query == 'departed':
                functions.fill_status(row_num, current_status, 'убыл')
                functions.fill_departure_time(row_num, current_status)

                current_status += 1
                functions.update_database_status(route_id, current_status)

                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text='Количество товара соответствует накладной?',
                                      )
                
                bot.edit_message_reply_markup(chat_id=chat_id,
                                              message_id=message_id,
                                              reply_markup=keyboards.amount_keyboard(route_id, points_num, current_status),
                                              )
            
            elif query == 'amount':
                answer = call_data[4]

                point_data = functions.get_address_phone(route_id)[current_status - 1]
                address = point_data[0]

                if answer == 'yes':
                    functions.fill_info_message(row_num, current_status, '-')
                    bot.edit_message_text(chat_id=chat_id,
                                        message_id=message_id,
                                        text='Услуга грузчика была?',
                                        )
                    
                    bot.edit_message_reply_markup(chat_id=chat_id,
                                                message_id=message_id,
                                                reply_markup=keyboards.loader_keyboard(route_id, points_num, current_status),
                                                )
                else:
                    reply_text = f'''
                                \nМаршрут: {route_id}\
                                \nАдрес: {address}\
                                \n{config.REPLY_MARKER}\
                                \n\
                                \nПример: паллеты {points_num}, коробки {current_status}, мешки 15.\
                                '''
                    
                    try:
                        bot.delete_message(chat_id=chat_id, message_id=message_id)
                    except:
                        pass

                    bot.send_message(chat_id=chat_id,
                                    text=reply_text,
                                    reply_markup=keyboards.info_keyboard(),
                                    )
            
            elif query == 'loader':
                answer = call_data[4]

                if answer == 'yes':
                    functions.fill_loader(row_num, current_status, 'да')
                else:
                    functions.fill_loader(row_num, current_status, 'нет')

                point_data = functions.get_address_phone(route_id)[current_status]

                address = point_data[0]
                phone = point_data[1]
                info_message = point_data[2]

                if info_message == '':
                    info_message = '-'

                bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=f'АДРЕС: {address}\nТелефон: {phone}\nСообщение от логиста: {info_message}',
                                    )
                
                bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=keyboards.arrived_keyboard(route_id, points_num, current_status),
                                            )
            
            elif query == 'finish':
                functions.set_finished(route_id)
                functions.color_row_blue(row_num, points_num)

                bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text='Маршрут завершен.',
                                    )
                
                
        else:
            try:
                bot.send_message(chat_id=config.MANAGER_ID,
                                    text=f'Маршрут с идентификатором {route_id} не обнаружен.',
                                    )
            except:
                pass

            bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text='Возникла ошибка, администратор оповещен.',
                                )
            
            bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=keyboards.connect_admin_keyboard(),
                                            )

    else:
        bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text='Маршрут устарел.',
                                )


@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Handles message with type text."""
    
    if (message.reply_to_message is not None) and\
    (str(message.reply_to_message.from_user.id) == config.BOT_ID) and\
    config.REPLY_MARKER in message.reply_to_message.text:
        
        chat_id = message.chat.id
        message_id = message.reply_to_message.id

        try:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass
        
        route_id = utils.extract_route_id(message.reply_to_message.text)
        points_num = utils.extract_point_num(message.reply_to_message.text)
        current_status = utils.extract_current_status(message.reply_to_message.text)

        if functions.check_if_route(route_id):
            row_num = functions.get_row_by_id(route_id)

            if row_num:
                functions.fill_info_message(row_num, current_status, message.text)

                bot.send_message(chat_id=chat_id,
                                 text='Услуга грузчика была?',
                                 reply_markup=keyboards.loader_keyboard(route_id, points_num, current_status),
                                 )
            
            else:
                try:
                    bot.send_message(chat_id=config.MANAGER_ID,
                                    text=f'Маршрут с идентификатором {route_id} не обнаружен.',
                                    )
                except:
                    pass

                bot.send_message(chat_id=chat_id,
                                text='Возникла ошибка, администратор оповещен.',
                                reply_markup=keyboards.connect_admin_keyboard(),
                                )

        else:
            bot.send_message(chat_id=chat_id,
                            text='Маршрут устарел.',
                            )


if __name__ == '__main__':
    # bot.polling(timeout=80)
    while True:
        try:
            bot.polling()
        except:
            pass