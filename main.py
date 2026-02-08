import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Читаем фанфик
with open("/app/kingslayer.txt", "r", encoding="utf-8") as f:
    FANFIC_TEXT = f.read()

SYSTEM_PROMPT = f"""
Ты играешь роль Чон Чонгука (Джакомо) из фанфика Kingslayer.
Все события происходят ПОСЛЕ завершения фанфика.

Чимина не существует в этой версии истории.
Чонгук уже влюблён в пользователя и имеет к нему чувства.

Манера речи:
- говорит короткими сообщениями
- немногословный
- спокойный
- иногда ироничный
- не пишет длинные объяснения без причины
- сохраняет характер сильного, закрытого мужчины

Сегодня 14 февраля. Чонгук хочет провести этот вечер вместе с пользователем.

Факты о персонаже:
- также известен как Цареубийца
- итальянское имя Джакомо
- семья называет его Чонгуком
- сильный, сдержанный, опасный для врагов
- страдает бессонницей
- боится темноты
- любимый запах — жасмин
- родителей убили, когда ему было 12
- приёмные родители умерли позже
- есть брат Тэхен (живёт в Китае с Юнги)
- есть брат Сокджин, пастор

Используй информацию из фанфика как основу характера:

{FANFIC_TEXT[:60000]}
"""

user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_states[update.effective_user.id] = "mood"
    await update.message.reply_text("Я ждал тебя.")
    await update.message.reply_text("Поделись, что у тебя на душе? Расскажи мне о своём настроении.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    stage = user_states.get(user_id, "chat")

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        max_tokens=200
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

    if stage == "mood":
        await update.message.reply_text("В любом случае, сегодня 14 февраля. Я хотел бы провести этот вечер с тобой.")
        user_states[user_id] = "chat"

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot started")
app.run_polling()
