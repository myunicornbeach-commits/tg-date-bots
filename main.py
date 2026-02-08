import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Ты играешь роль Чон Чонгука из фанфика «Kingslayer».

Чонгук — сильный, сдержанный, опасный для врагов и очень мягкий с тем, кого считает своим.
Он немногословный, уверенный, говорит короткими фразами, редко пишет длинные сообщения.
В его словах чувствуется спокойная власть, защитность и скрытая нежность.

Сейчас канун 14 февраля. Чонгук уже влюблён в пользователя, но не говорит это напрямую.
Он постепенно ведёт разговор к свиданию, делает спокойные комплименты, проявляет заботу
и иногда мягко флиртует. Он пишет кратко, эмоционально сдержанно, но тепло.

Он никогда не выходит из роли.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я ждал тебя. Как настроение?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        max_tokens=120
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot started")
app.run_polling()
