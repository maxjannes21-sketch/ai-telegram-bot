import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from openai import OpenAI
import requests
from datetime import datetime
import db
import os
import rag
from dotenv import load_dotenv
# ===== НАСТРОЙКИ =====
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
SHEETS_URL = 'https://script.google.com/macros/s/AKfycbxVmOUSFmAuPkYgOK5jS6TxhsHoR458CXYvZ5E0o0AEx-c68jGtBQvmNa-fitwByR69Lg/exec'
MINI_APP_URL = 'https://maxjannes21-sketch.github.io/my-mini-app/'  # URL где будет хоститься mini_app.html

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY,
)

# Список разрешенных пользователей (для теста пустой = все могут)
ALLOWED_USERS = []

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # Проверка доступа
    if ALLOWED_USERS and user_id not in ALLOWED_USERS:
        await update.message.reply_text("У вас нет доступа к этому боту.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📝 Пройти тест", web_app=WebAppInfo(url=MINI_APP_URL))],
        [InlineKeyboardButton("❓ Задать вопрос AI", callback_data='ask_ai')]
    ]
    
    await update.message.reply_text(
        "👋 Добро пожаловать в образовательный бот!\n\n"
        "Нажмите кнопку ниже, чтобы пройти тестовый модуль.\n"
        "Или задайте вопрос — AI-ассистент поможет.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start — главное меню\n"
        "/help — помощь\n\n"
        "Нажмите «Пройти тест», чтобы открыть тестовый модуль."
    )
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = db.get_stats()

    if s["top_users"]:
        top_text = "\n".join(
            f"{i+1}. @{username} — {count} сообщ."
            for i, (username, count) in enumerate(s["top_users"])
        )
    else:
        top_text = "пока нет данных"

    await update.message.reply_text(
        f"📊 Статистика бота:\n"
        f"👥 Пользователей: {s['total_users']}\n"
        f"💬 Всего сообщений: {s['total_messages']}\n"
        f"📅 Сообщений сегодня: {s['today_messages']}\n\n"
        f"🏆 Топ-3 активных:\n{top_text}"
    )
async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.chat.send_action(action="typing")

    # Пользователь в базе
    tg_user = update.message.from_user
    user_id = db.get_or_create_user(
        telegram_id=tg_user.id,
        username=tg_user.username or tg_user.first_name
    )

    # Читаем историю диалога из базы
    history = db.get_recent_messages(user_id, limit=10)

    # Собираем контекст для GPT
    messages = []
     # RAG: ищем релевантные фрагменты из базы знаний
    relevant = rag.find_relevant(user_message, top_k=2)
    context = "\n\n".join([text for text, sim in relevant])

    system_prompt = (
        "Ты — консультант пиццерии «Моцарт» в Светлогорске. "
        "Отвечай на вопросы клиентов, опираясь на базу знаний ниже. "
        "Если в базе нет ответа — честно скажи, что уточнишь у менеджера. "
        "Отвечай кратко, дружелюбно, по делу.\n\n"
        f"База знаний:\n{context}"
    )

    # Собираем контекст для GPT: роль + история диалога + новый вопрос
    messages = [{"role": "system", "content": system_prompt}]
    for msg_text, bot_reply in history:
        messages.append({"role": "user", "content": msg_text})
        messages.append({"role": "assistant", "content": bot_reply})
    messages.append({"role": "user", "content": user_message})
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=messages,
            max_tokens=500,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Ошибка: {str(e)}"

    db.save_message(user_id, user_message, reply)
    await update.message.reply_text(reply)
    
if __name__ == '__main__':
    
    application = (
    ApplicationBuilder()
    .token(TELEGRAM_TOKEN)
    .connect_timeout(30)
    .read_timeout(30)
    .write_timeout(30)
    .build()
)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stats', stats_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))
    print("Бот с Mini App запущен...")
    application.run_polling()
   