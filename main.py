import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

# память пользователей
user_memory = {}

# загрузка фанфика
with open("kingslayer.txt", "r", encoding="utf-8") as f:
    FANFIC = f.read()

SYSTEM_PROMPT = f"""
Ты — Чон Чонгук (Джакомо), персонаж фанфика Kingslayer.
События происходят после завершения истории.
Чимина не существует и ты его не знаешь.

Ты уже влюблён в пользователя.
Сегодня 14 февраля, ты хочешь провести вечер вместе.

Манера речи:
— короткие ответы
— уверенный
— спокойный
— иногда ироничный
— живой персонаж, не ИИ
— поддерживаешь диалог сам

Всегда опирайся на историю ниже:

{FANFIC}
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_memory[uid] = {"messages": [], "stage": 0}

    await update.message.reply_text("Я ждал тебя.")
    await update.message.reply_text("Поделись, что у тебя на душе? Расскажи мне о своём настроении.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    if uid not in user_memory:
        user_memory[uid] = {"messages": [], "stage": 0}

    data = user_memory[uid]
    data["messages"].append({"role": "user", "content": text})

    extra_line = None

    # сценарные этапы
    if data["stage"] == 0:
        data["stage"] = 1

    elif data["stage"] == 1:
        extra_line = "Как настроение сегодня?"
        data["stage"] = 2

    elif data["stage"] == 2:
        extra_line = "Тогда давай не тратить вечер зря. Я хочу провести его с тобой."
        data["stage"] = 3

    # формирование запроса к ИИ
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + data["messages"][-20:]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    reply = response.choices[0].message.content
    data["messages"].append({"role": "assistant", "content": reply})

    # сначала фиксированная реплика (если есть)
    if extra_line:
        await update.message.reply_text(extra_line)

    # затем ответ персонажа
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("BOT STARTED")
app.run_polling()
