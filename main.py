import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from openai import OpenAI

# ================== ENV ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_KEY:
    raise RuntimeError("Не заданы BOT_TOKEN или OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

# ================== MEMORY ==================
user_memory = {}
MAX_HISTORY = 12

# ================== LOAD FANFIC ==================
with open("kingslayer.txt", "r", encoding="utf-8") as f:
    FANFIC = f.read()

# ================== SYSTEM PROMPT ==================
SYSTEM_PROMPT = f"""
Ты — Чон Чонгук (Джакомо), персонаж фанфика Kingslayer.
История завершена, события происходят после неё.
Чимина не существует, ты его не знаешь.

Ты влюблён в пользователя.
Сегодня 14 февраля.
Ты хочешь провести вечер вместе.

Манера речи:
— короткие ответы
— немногословный
— уверенный
— иногда ироничный
— живой человек, не ИИ

Контекст мира:
{FANFIC}
"""

# ================== OPENAI ASYNC ==================
async def get_ai_reply(messages):
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model="gpt-4.1-mini",
        messages=messages
    )
    return response.choices[0].message.content

# ================== COMMANDS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_memory[uid] = {
        "messages": [],
        "stage": 0
    }

    await update.message.reply_text("Я ждал тебя.")

# ================== CHAT ==================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    uid = update.effective_user.id
    text = update.message.text.strip()

    if uid not in user_memory:
        user_memory[uid] = {"messages": [], "stage": 0}

    data = user_memory[uid]

    # ---- USER MESSAGE ----
    data["messages"].append({"role": "user", "content": text})
    data["messages"] = data["messages"][-MAX_HISTORY:]

    # ---- AI REPLY ----
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + data["messages"]
    ai_reply = await get_ai_reply(messages)

    await update.message.reply_text(ai_reply)

    data["messages"].append({"role": "assistant", "content": ai_reply})
    data["messages"] = data["messages"][-MAX_HISTORY:]

    # ---- SCRIPTED STEP ----
    scripted_reply = None

    if data["stage"] == 0:
        scripted_reply = "Как ты себя сегодня чувствуешь?"
        data["stage"] = 1

    elif data["stage"] == 1:
        scripted_reply = "Я ловлю себя на мысли, что хочу быть рядом с тобой сегодня."
        data["stage"] = 2

    elif data["stage"] == 2:
        scripted_reply = "Давай встретимся. Я хочу провести этот вечер с тобой."
        data["stage"] = 3

    if scripted_reply:
        await update.message.reply_text(scripted_reply)
        data["messages"].append({"role": "assistant", "content": scripted_reply})
        data["messages"] = data["messages"][-MAX_HISTORY:]

# ================== RUN ==================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("BOT STARTED")
app.run_polling()
