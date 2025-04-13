import os
import re
import telebot
from telebot import types
from dotenv import load_dotenv
import signal
import sys
from analyzer import Analyzer
from message_processor import MessageProcessor
from text_processor import TextProcessor
from db import Database
from search_engine import SearchEngine
load_dotenv('.env')

textProcessor = TextProcessor()
messageProcessor = MessageProcessor()
db = Database()
searchEngine = SearchEngine(textProcessor)
analyzer = Analyzer(textProcessor, db, searchEngine)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN not found! Check the .env file.")

bot = telebot.TeleBot(BOT_TOKEN)
URL_PATTERN = re.compile(r'https?://\S+')
user_languages = {}  # user_id -> language code
user_initialized = set()  # user_ids who have already selected a language

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    if user_id not in user_initialized:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton("English"), types.KeyboardButton("Українська"))
        bot.send_message(
            message.chat.id,
            "🌐 Please choose your language / Будь ласка, оберіть мову:",
            reply_markup=markup
        )
    else:
        lang = user_languages.get(user_id, 'en')
        messageProcessor.set_language(lang)
        bot.send_message(message.chat.id, messageProcessor.messages.get("WELCOME_MESSAGE", "Welcome!"), parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def help_message(message):
    lang = user_languages.get(message.from_user.id, 'en')
    messageProcessor.set_language(lang)
    bot.send_message(message.chat.id, messageProcessor.messages.get("HELP_MESSAGE"), parse_mode="Markdown")

@bot.message_handler(commands=['language'])
def change_language(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("English", callback_data="lang_en"),
        types.InlineKeyboardButton("Українська", callback_data="lang_uk")
    )
    bot.send_message(
        message.chat.id,
        "🌐 Select your language:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def handle_language_callback(call):
    lang = call.data.split("_")[1]
    user_languages[call.from_user.id] = lang
    user_initialized.add(call.from_user.id)
    messageProcessor.set_language(lang)
    bot.send_message(call.message.chat.id, messageProcessor.messages.get("WELCOME_MESSAGE", "Welcome!"), parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text in ["English", "Українська"])
def set_language(message):
    lang = 'en' if message.text == "English" else 'uk'
    user_languages[message.from_user.id] = lang
    user_initialized.add(message.from_user.id)
    messageProcessor.set_language(lang)
    bot.send_message(message.chat.id, messageProcessor.messages.get("WELCOME_MESSAGE", "Welcome!"), parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    lang = user_languages.get(user_id, 'en')  # default to English
    messageProcessor.set_language(lang)
    user_input = message.text.strip()

    try:
        if URL_PATTERN.match(user_input):
            news_score, source_score, provoking_score = analyzer.verify_news_by_link(user_input)
            response = messageProcessor.link_analysis(news_score, source_score, provoking_score)
        else:
            news_score, provoking_score = analyzer.verify_news_by_text(user_input)
            response = messageProcessor.text_analysis(news_score, provoking_score)
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    except Exception as e:
        print(f"Error: {e}")
        bot.send_message(message.chat.id, messageProcessor.messages.get("ERROR_MESSAGE", "Something went wrong. Try again later."))

def handle_exit(signum, frame):
    print("\nShutting down... Stopping the bot.")
    bot.stop_polling()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

try:
    print("Bot is running! Press Ctrl + C to stop.")
    bot.infinity_polling()
except KeyboardInterrupt:
    handle_exit(None, None)
