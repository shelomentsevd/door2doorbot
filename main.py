#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging
import requests

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

(CHOOSING, REPORT, ADDRESS, EDIT_ADDRESS, APARTMENTS_AMOUNT, EDIT_APARTMENTS_AMOUNT, 
APARTMENTS_OPENED, EDIT_APARTMENTS_OPENED, COMMENT, EDIT, ABANDON, FINISHED) = range(12)

main_keyboard = [['Начать отчет'],
                  ['Помощь'],
                  ['О программе']]

mainKeyboardMarkup = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=True)

def start(bot, update):
    update.message.reply_text(
        "Привет!"
        "Я программа для отчетов по проекту \"Door to door\" <сайт проекта>.\n"
        "Что бы начать отчет по дому, нажми кнопку \"Создать отчет\" или пришли гео координаты дома.\n"
        "Помощь по программе доступна по команде /help.\n"
        "Связаться с разработчиками можно через контакты указанные в /about\n",
        reply_markup=mainKeyboardMarkup
    )

    return CHOOSING

def new_report(bot, update):
    update.message.reply_text(
        "Отправьте, пожалуйста, локацию дома"
    )
    return ADDRESS

def show_help(bot, update):
    update.message.reply_text(
        "Что бы начать отчет по дому, нажми кнопку \"Создать отчет\" или пришли гео координаты дома."
        "Помощь по программе доступна по команде /help."
        "Связаться с разработчиками можно через контакты указанные в /about."
    )
    return CHOOSING

def show_about(bot, update):
    update.message.reply_text(
        "Тут будет текст О программе"
    )
    return CHOOSING

def address_input(bot, update, user_data):
    # TODO: Check if report already exist
    address = {
        "coordinates": [update.message.location.latitude, update.message.location.longitude]
    }
    user_data['address'] = address
    update.message.reply_text(
        "Введите кол-во пройденных квартир"
    )
    return APARTMENTS_AMOUNT

def apartments_amount_input(bot, update, user_data):
    user_data['apartments'] = dict()
    # TODO: Check integer
    user_data['apartments']['all'] = update.message.text
    update.message.reply_text(
        "Сколько квартир открыли?"
    )
    return APARTMENTS_OPENED

def apartments_opened_input(bot, update, user_data):
    user_data['apartments']['opened'] = update.message.text
    update.message.reply_text(
        "Оставьте комментарий по дому"
    )
    return COMMENT

edit_keyboard = [['Адресс'],
                  ['Квартир пройдено'],
                  ['Квартир открыло'],
                  ['Отправить']]

editKeyboardMarkup = ReplyKeyboardMarkup(edit_keyboard, one_time_keyboard=True)

def comment_input(bot, update, user_data):
    user_data['comment'] = update.message.text
    update.message.reply_text(
        "Спасибо за ваш отчет.\nВот данные которые вы предоставили:"
    )
    update.message.reply_text(user_data)
    update.message.reply_text(
        "Выберите в меню то, что хотите отредактировать или нажмите \"Отправить\""
        ", что бы отправить отчет.",
        reply_markup=editKeyboardMarkup
    )

    return EDIT

def edit_field(bot, update, user_data):
    field = update.message.text
    if field == u"Квартир пройдено":
        update.message.reply_text("Введите количество пройденных квартир")
        return EDIT_APARTMENTS_AMOUNT
    if field == u"Квартир открыло":
        update.message.reply_text("Введите количество квартир с хозяевами которых удалось пообщаться")
        return EDIT_APARTMENTS_OPENED
    elif field == u"Адресс":
        update.message.reply_text("Отправьте локацию дома")
        return EDIT_ADDRESS
    elif field == u"Отправить":
        update.message.reply_text("Данные отправлены, спасибо за ваш труд!", reply_markup=mainKeyboardMarkup)
        # TODO: Send data to server, clear temporary data. All async
        user_data['userId'] = update.message.chat['id']
        user_data['username'] = update.message.chat['username']
        user_data['address']['name'] = "Адресс"
        print user_data
        r = requests.post("https://door-to-door-api.herokuapp.com/api/v1/building", data=user_data)
        return CHOOSING
    update.message.reply_text("Вы не можете отредактировать: %s" % field)
    return EDIT

def show_edit_message(update, user_data):
    update.message.reply_text("Данные отредактированы.\nТекущий отчет выглядит так:")
    update.message.reply_text(user_data)
    update.message.reply_text(
        "Выберите в меню то, что хотите отредактировать или нажмите \"Отправить\""
        ", что бы отправить отчет.",
        reply_markup=editKeyboardMarkup
    )

def edit_address(bot, update, user_data):
    address = {
        "coordinates": [update.message.location.latitude, update.message.location.longitude]
    }
    user_data['address'] = address
    show_edit_message(update, user_data)
    return EDIT

def edit_apartments_amount(bot, update, user_data):
    # TODO: Check integer
    user_data['apartments']['all'] = update.message.text
    show_edit_message(update, user_data)
    return EDIT

def edit_apartments_opened(bot, update, user_data):
    user_data['apartments']['opened'] = update.message.text
    show_edit_message(update, user_data)
    return EDIT

def done(bot, update, user_data):
    # TODO: Handle fallbacks properly
    print "fallback"
    print update.message.text
    return CHOOSING

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("431912337:AAEobNaW1QN9bNfLgVKTN05n2ufzdQaWRvc")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states = {
            CHOOSING: [
                RegexHandler(u'^Начать отчет$', new_report),
                RegexHandler(u'^Помощь$', show_help),
                RegexHandler(u'^О программе$', show_about)
            ],
            ADDRESS: [
                MessageHandler(Filters.location, address_input, pass_user_data=True)
            ],
            APARTMENTS_AMOUNT: [
                MessageHandler(Filters.text, apartments_amount_input, pass_user_data=True)
            ],
            APARTMENTS_OPENED: [
                MessageHandler(Filters.text, apartments_opened_input, pass_user_data=True)
            ],
            COMMENT: [
                MessageHandler(Filters.text, comment_input, pass_user_data=True)
            ],
            EDIT: [
                RegexHandler(u'^(Адресс|Квартир пройдено|Квартир открыло|Отправить)$', edit_field, pass_user_data=True)
            ],
            EDIT_ADDRESS: [
                MessageHandler(Filters.location, edit_address, pass_user_data=True)
            ],
            EDIT_APARTMENTS_AMOUNT: [
                MessageHandler(Filters.text, edit_apartments_amount, pass_user_data=True)
            ],
            EDIT_APARTMENTS_OPENED: [
                MessageHandler(Filters.text, edit_apartments_opened, pass_user_data=True)   
            ]
        },

        fallbacks=[RegexHandler('^Done$', done, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
