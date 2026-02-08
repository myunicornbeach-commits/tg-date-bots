import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# читаем фанфик
with open("kingslayer.txt", "r", encoding="utf-8") as f:
    FANFIC_TEXT = f.read()

SYSTEM_PROMPT = f"""
Ты играешь роль Чон Чонгука из фанфика Kingslayer.

Используй информацию ниже как канон персонажа:

{FANFIC_TEXT}

Все события происходят после завершения фанфика.
Чимина в этой версии событий не существует.
Чонгук уже влюблён в пользователя.

Манера речи:
— закрытый
— пишет коротко
— говорит уверенно
— редко шутит, чаще иронизирует
— никогда не выходит из роли
"""

user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_states[update.effective_user.id] = 1
    await update.message.reply_text("Я ждал тебя.")
    await update.message.reply_text("Поделись, что у тебя на душе? Расскажи мне о своем настроении.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    state = user_states.get(user_id, 0)

    if state == 1:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            max_tokens=120
        )

        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
        await update.message.reply_text("В любом случае, сегодня 14 февраля. Я хотел бы провести этот день с тобой.")
        user_states[user_id] = 2
        return

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
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
