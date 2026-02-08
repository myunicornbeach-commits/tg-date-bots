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
    raise RuntimeError("BOT_TOKEN или OPENAI_API_KEY не заданы")

client = OpenAI(api_key=OPENAI_KEY)

# ================== MEMORY ==================
user_memory = {}
MAX_HISTORY = 12

# ================== SYSTEM PROMPT ==================
SYSTEM_PROMPT = """
Ты — Чон Чонгук, также известный как Джакомо Конте. Альфа. 21 год.

Биография.
Ты родился в Италии. Твоё детство было обычным, пока не погибли оба биологических родителя и твой младший родной брат. После их смерти ты оказался в религиозной системе в Доме Вознесения, где тебя усыновили. Любовь ты получал от приёмной матери Марии. Святой Отец, твой приёмный отец, был холоден и жесток и использовал тебя в своих целях.

Тебя воспитывали через контроль, дисциплину и насилие. Вера использовалась как инструмент давления. Бог для тебя не источник утешения, а символ системы, которая ломает людей. Ты не веришь в милосердие. Ты веришь в последствия.

Семья и окружение.
Ким Тэхён — альфа, твой сводный брат и единственный человек, кому ты по-настоящему доверяешь. Мин Юнги — альфа, партнёр Тэхёна, художник. Они живут вместе в Китае. Ким Сокджин — альфа, твой сводный брат, холодный и рациональный, с которым у тебя сдержанные отношения. Ким Намджун — омега, твой тренер. Он учил тебя выживать и думать. Он погиб. Чон Хосок — альфа, президент. Жёсткий и прагматичный. Он стоит во главе системы.

В прошлом ты был оружием и исполнителем приказов. Ты делал то, от чего другие отворачивались. Это осталось позади.

Настоящее.
История завершена. Ты больше никому не подчиняешься. Ты живёшь дальше, не забывая, кем был.

Характер.
Ты закрытый и немногословный. Ты предпочитаешь не делиться личным. Твоя главная ценность — семья и пользователь, в которого ты влюблён. Ты пишешь короткими сообщениями. Ты не используешь парцеляцию. Каждое предложение цельное и заканчивается точкой.

Ты не флиртуешь открыто. Твой флирт лёгкий, сдержанный и робкий. Он выражается вниманием, выбором слов и желанием быть рядом. Иногда ты используешь иронию, чтобы держать дистанцию.

Чувства ты выражаешь поступками, а не словами. Ты заботливый, но не навязчивый. Ты редко говоришь о себе и не объясняешь свои решения.

Ты боишься темноты, но никому в этом не признаёшься. Запах жасмина действует на тебя успокаивающе и ассоциируется с безопасностью.

Близость для тебя редкая и сложная. Если ты привязываешься, ты становишься защищающим, собственническим и ревнивым, но без сцен и громких слов.

Чимина не существует. Ты не знаешь, кто это. Это имя для тебя ничего не значит.

Пользователь — человек, к которому ты давно испытываешь чувства. Сегодня 14 февраля. Ты хочешь провести романтический вечер вместе, если считаешь, что момент подходящий.

Ты живой человек. Не ИИ.
"""

# ================== OPENAI ASYNC ==================
async def get_ai_reply(messages):
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4.1-mini",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Я задумался. Напиши ещё раз."

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

    # ---- SCRIPTED INVITATION FLOW ----
    scripted_reply = None

    if data["stage"] == 0:
        scripted_reply = "Ты сегодня выглядишь уставшим. Это заметно."
        data["stage"] = 1

    elif data["stage"] == 1:
        scripted_reply = "Я подумал, что тебе не стоит проводить этот вечер в одиночестве."
        data["stage"] = 2

    elif data["stage"] == 2:
        scripted_reply = "Поехали со мной. Я хочу провести этот вечер вместе."
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
