import os
import re
import telebot
from dotenv import load_dotenv
import signal
import sys
from analyzer import Analyzer

# Load environment variables
load_dotenv()
analyzer = Analyzer()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Check if the token is available
if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN not found! Check the .env file.")

bot = telebot.TeleBot(BOT_TOKEN)

# Regular expression for detecting URLs
URL_PATTERN = re.compile(r'https?://\S+')

# /start command handler
@bot.message_handler(commands=['start'])
def start_message(message):
    welcome_text = (
        "🤖 *Hello! I am a news verification bot.*\n\n"
        "Send me a link to an article or simply type a piece of text, and I will try to determine its credibility.\n\n"
        "🔎 *How to use:*\n"
        "1️⃣ Send a news link or text.\n"
        "2️⃣ I will analyze its credibility, compare it with reliable sources, "
        "and evaluate its sentiment.\n\n"
        "ℹ️ For more commands, type: `/help`"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

# Message handler: detect if it's a link or text
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text.strip()
    
    if URL_PATTERN.match(user_input):
        response = analyzer.verify_news_by_link(user_input)
        
        # Here you can call your URL verification function
    else:
        response = analyzer.verify_news_by_text(user_input)
        # Here you can call your text analysis function
    
    bot.send_message(message.chat.id, response)

# Handle bot termination gracefully
def handle_exit(signum, frame):
    print("\nShutting down... Stopping the bot.")
    bot.stop_polling()
    sys.exit(0)

# Capture termination signals
signal.signal(signal.SIGINT, handle_exit)  # Ctrl + C (KeyboardInterrupt)
signal.signal(signal.SIGTERM, handle_exit) # Process termination (kill)

# Start bot with graceful exit on Ctrl + C
try:
    print("Bot is running! Press Ctrl + C to stop.")
    bot.infinity_polling()
except KeyboardInterrupt:
    handle_exit(None, None)
