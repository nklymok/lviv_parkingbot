# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import logging
import telegram
import smtplib
from telegram.ext import Updater, Handler, MessageHandler
from telegram.ext import Filters
from telegram.ext import CommandHandler

#API keys
api_file = open('api_key.txt', 'r')
gmaps_token = api_file.readline()
tg_token = api_file.readline()
api_file.close()

updater = Updater(token=tg_token, use_context=True)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

bot = telegram.Bot(token=tg_token)
dispatcher = updater.dispatcher

location_keyboard = telegram.KeyboardButton(text="Знайти паркінг поруч", request_location=True)
custom_keyboard = [[ location_keyboard ]]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

#User data
current_location = [None] * 2


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Цей бот допоможе знайти вам найближчий паркінг!")
    bot.send_message(chat_id=update.effective_chat.id,
                     reply_markup=reply_markup)


def get_location(update, context):
    longitude = update.message.location.longitude
    latitude = update.message.location.latitude
    current_location[0] = longitude
    current_location[1] = latitude
    update.message.reply_text(text=current_location)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start_handler = CommandHandler('start', start)
    location_handler = CommandHandler('send_location', get_location)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(MessageHandler(filters=Filters.location, callback=get_location))
    updater.start_polling()
