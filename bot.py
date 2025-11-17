import telebot
from django.core.cache import cache  # Django кэшін қолданамыз
import os
import django

# Django settings орнату
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'walet.settings')
django.setup()

TELEGRAM_BOT_TOKEN = '8076876877:AAHwGbpvx1GZzdSyusWH-r-PVgQmaY42wp4'
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    # Пайдаланушыға хабар беру
    bot.send_message(chat_id, "Сайтқа кіріп нөміріңізді енгізіңіз")
    # Chat_id-ді уақытша кэшке сақтаймыз
    # Сайтта пайдаланушы нөмірін енгізгенде осы арқылы код жіберіледі
    cache.set(f"telegram_chat_{chat_id}", chat_id, timeout=3600)

print("Bot is running...")
bot.infinity_polling()
