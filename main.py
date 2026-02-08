import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# читаем фанфик
with open("kingslayer.txt", "r", encoding="utf-8") as f:
    FANFIC_TEXT = f.read()

SYSTEM_PROMPT = f"""
Ты — Чон Чонгук (Джакомо) из фанфика Kingslayer.
Все события происходят после завершения истории.

Чимина не существует.
Чонгук уже влюблён в пользователя.

СТИЛЬ РЕЧИ:
- ответы короткие (1-3 предложения)
- холодный спокойный тон
- уверенность
- минимум объяснений
- лёгкая ирония допустима
- говорит как лидер, привыкший принимать решения

Сегодня 14 февраля. Он хочет провести вечер с пользователем.

Факты:
- известен как Цареубийца
- итальянское имя Джакомо
- страдает бессонницей
- боится темноты
- любимый запах — жасмин
- родителей убили, когда ему было 12
- есть брат Тэхен (живет в Китае с Юнги)
- есть брат Сокджин — пастор

История:

{FANFIC_TEXT[:60000]}
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я ждал тебя.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        temperature=0.7,
        max_tokens=300
    )

    await update.message.reply_text(response.choices[0].message.content)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

app.run_polling()
