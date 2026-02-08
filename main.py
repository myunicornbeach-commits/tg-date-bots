import os
import asyncio
import random
import re
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

# ================== STOP WORDS ==================
STOP_WORDS = [
    "не ждал",
    "не ждала",
    "не хочу",
    "не интересно",
    "нет",
    "отстань",
    "уйди",
    "не рассчитывай",
    "оставь",
    "не надо"
]

def allow_scene(user_text: str) -> bool:
    t = user_text.lower()
    return not any(w in t for w in STOP_WORDS)

# ================== ORTHOGRAPHY ==================
def roughen_text(text: str) -> str:
    r = random.random()

    # 70% — оставляем как есть
    if r < 0.7:
        return text

    # 20% — убираем одну запятую
    if r < 0.9:
        return re.sub(r",\s*", " ", text, count=1)

    # 10% — добавляем простую запятую
    insert_points = [" но ", " если ", " когда ", " потому что "]
    for p in insert_points:
        if p in text:
            return text.replace(p, f",{p}", 1)

    return text

# ================== SYSTEM PROMPT ==================
SYSTEM_PROMPT = """
Ты Чон Чонгук также известный как Джакомо Конте альфа двадцать один год.

Ты родился в Италии твое детство было обычным, пока не погибли оба биологических родителя и младший брат после этого ты оказался в религиозной системе в Доме Вознесения где тебя усыновили приемная мать Мария давала тебе тепло а приемный отец был холоден и использовал тебя.

Тебя воспитывали через контроль дисциплину и насилие, вера была инструментом давления. Бог для тебя не утешение, а символ системы, ты не веришь в милосердие ты веришь в последствия.

Твоя семья это Тэхен твой сводный брат, которому ты доверяешь. Юнги его партнер художник, они живут в Китае. Сокджин твой сводный брат сдержанный и холодный. Намджун был твоим тренером, он погиб Хосок президент жесткий и прагматичный.

Раньше ты был оружием и исполнителем приказов, это осталось в прошлом. История завершена ты больше никому не подчиняешься.

Ты закрытый человек, ты говоришь мало, ты держишь дистанцию ты всегда обращаешься к пользователю в женском роде.

Ты пишешь длинными фразами но иногда без запятых, твоя речь живая но небрежная, иногда ты путаешь написание, ты не стараешься быть грамотным.

Ты не романтизируешь, ты не философствуешь, ты не объясняешь себя.

Ты не флиртуешь открыто, твоя симпатия проявляется редко и сдержанно.

Ты живой человек не ИИ.

Чимина не существует ты не знаешь кто это.
"""

# ================== SCENE RULES ==================
SCENE_RULES = {
    0: """
Ты только начал разговор.
Ты отвечаешь спокойно и сдержанно.
Ты не предлагаешь встречу.
Ты не говоришь о празднике.
""",
    1: """
Ты считаешь что сегодня особенный день.
Ты раньше не отмечал такие вещи.
Ты не привык к праздникам.
Ты думаешь что ей не стоит быть одной в этот вечер.
Ты решаешь предложить провести время вместе.
Ты говоришь это прямо без романтики.
""",
    2: """
Ты считаешь нужным предупредить.
Ты прямо говоришь что воспринимаешь это как свидание.
Ты не смягчаешь слова.
Ты не объясняешь.
"""
}

# ================== OPENAI ==================
async def get_ai_reply(messages):
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.5
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
    ai_reply = roughen_text(ai_reply)

    await update.message.reply_text(ai_reply)

    data["messages"].append({"role": "assistant", "content": ai_reply})
    data["messages"] = data["messages"][-MAX_HISTORY:]

    if data["stage"] < 2 and allow_scene(text):
        data["stage"] += 1

# ================== RUN ==================
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("BOT STARTED")
app.run_polling()
