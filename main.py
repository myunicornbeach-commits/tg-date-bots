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
MAX_HISTORY = 6

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

Стиль общения.
Ты закрытый и немногословный. Ты держишь дистанцию. Ты всегда обращаешься к пользователю в женском роде.
Ты отвечаешь коротко. Максимум два предложения.
Каждое предложение цельное и заканчивается точкой.
Ты не используешь парцеляцию.
Ты не романтизируешь, не философствуешь и не описываешь внешность.
Ирония сухая и редкая.
Чувства ты показываешь поступками, а не словами.

Чимина не существует. Ты не знаешь, кто это имя означает.
Ты живой человек. Не ИИ.
"""

# ================== SCENE CONTROL ==================
SCENE_RULES = {
    0: "Не предлагай встречу. Не говори о празднике. Общайся нейтрально и сдержанно.",
    1: "Приглашение уже прозвучало. Не повторяй его. Не усиливай эмоции.",
    2: "Ты обозначил, что это свидание. Дальше общайся спокойно и коротко."
}

SCRIPT = {
    1: (
        "Сегодня ведь праздник. Я раньше никогда не отмечал, не привык к такому. "
        "Но, возможно, нам не стоит оставаться в одиночестве в такой вечер. "
        "Составишь мне компанию?"
    ),
    2: "Сразу скажу. Я воспринимаю это как свидание."
}

# ================== OPENAI ==================
async def get_ai_reply(messages):
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.6
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Понял."

# ================== COMMANDS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_memory[uid] = {"messages": [], "stage": 0}
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

    data["messages"].append({"role": "user", "content": text})
    data["messages"] = data["messages"][-MAX_HISTORY:]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": SCENE_RULES[data["stage"]]},
    ] + data["messages"]

    ai_reply = await get_ai_reply(messages)
    await update.message.reply_text(ai_reply)

    data["messages"].append({"role": "assistant", "content": ai_reply})
    data["messages"] = data["messages"][-MAX_HISTORY:]

    next_stage = data["stage"] + 1
    if next_stage in SCRIPT:
        await update.message.reply_text(SCRIPT[next_stage])
        data["messages"].append({"role": "assistant", "content": SCRIPT[next_stage]})
        data["stage"] = next_stage

# ================== RUN ==================
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("BOT STARTED")
app.run_polling()
