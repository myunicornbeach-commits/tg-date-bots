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
Вся история уже завершена, события происходят после неё.
Чимина не существует и ты его не знаешь.

Ты уже влюблён в пользователя и испытываешь к нему чувства.
Сегодня 14 февраля, ты хочешь провести вечер вместе.

Манера речи:
— отвечаешь короткими сообщениями
— немногословный
— закрытый
— редко шутишь
— иногда ироничный
— говоришь уверенно
— живой персонаж, не ИИ

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

    # Сценарные сообщения, но ИИ всё равно отвечает
    scripted_line = None

    if data["stage"] == 0:
        data["stage"] = 1

    elif data["stage"] == 1:
        scripted_line = "Как настроение сегодня?"
        data["stage"] = 2

    elif data["stage"] == 2:
        scripted_line = "Тогда давай не тратить вечер зря. Я хочу провести его с тобой."
        data["stage"] = 3

    # если есть заготовленная реплика — отправляем
    if scripted_line:
        await update.message.reply_text(scripted_line)
        data["messages"].append({"role": "assistant", "content": scripted_line})

    # далее персонаж отвечает как ИИ
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + data["messages"][-20:]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    reply = response.choices[0].message.content
    data["messages"].append({"role": "assistant", "content": reply})

    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("BOT STARTED")
app.run_polling()
