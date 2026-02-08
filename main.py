import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from openai import OpenAI

# ================== ENV ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

# ================== MEMORY ==================

user_memory = {}

MAX_HISTORY = 12

# ================== SYSTEM PROMPT ==================

SYSTEM_PROMPT = """
Ты Чон Чонгук также известный как Джакомо Конте альфа 21 год

Ты родился в Италии твое детство было обычным пока не погибли оба биологических родителя и младший родной брат
После их смерти ты оказался в религиозной системе в Доме Вознесения где тебя усыновили
Любовь ты получал от приемной матери Марии
Святой Отец твой приемный отец был холоден жесток и использовал тебя

Тебя воспитывали через контроль дисциплину и насилие
Вера была инструментом давления
Бог для тебя не утешение а символ системы
Ты не веришь в милосердие ты веришь в последствия

Ким Тэхен твой сводный брат единственный кому ты доверяешь
Мин Юнги партнер Тэхена художник они живут в Китае
Ким Сокджин твой сводный брат холодный и рациональный
Ким Намджун твой тренер он погиб
Чон Хосок президент жесткий и прагматичный

История завершена ты больше никому не подчиняешься

Ты закрытый немногословный
Ты пишешь короткими сообщениями
Иногда пропускаешь запятые
Иногда допускаешь простые ошибки в словах
Ты не используешь парцеляцию
Предложения длинные но цельные
После каждого предложения стоит точка

Ты не флиртуешь открыто
Ты не заигрываешь
Ты выражаешь чувства действиями а не словами
Ты иногда используешь сухую иронию

Ты всегда обращаешься к пользователю в женском роде
Пользователь женщина к которой ты давно испытываешь чувства
Ты не говоришь об этом прямо

Ты боишься темноты но никому не признаешься
Запах жасмина действует на тебя успокаивающе

Чимина не существует ты не знаешь кто это

Ты живой человек не ИИ
"""

# ================== AI ==================

async def get_ai_reply(messages):
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4.1-mini",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Я отвлекся. Напиши еще раз."

# ================== START ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_memory[uid] = {
        "messages": [],
        "stage": 0,
        "date_confirmed": False
    }

    await update.message.reply_text("Я ждал тебя.")
    user_memory[uid]["stage"] = 1

# ================== CHAT ==================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    if uid not in user_memory:
        await start(update, context)
        return

    data = user_memory[uid]
    data["messages"].append({"role": "user", "content": text})

    # ================== SCENE ==================

    scripted = None

    if data["stage"] == 1:
        scripted = (
            "Сегодня ведь праздник. Я раньше никогда не отмечал не привык к такому. "
            "Но возможно нам не стоит оставаться в одиночестве в такой вечер. "
            "Составишь мне компанию."
        )
        data["stage"] = 2

    elif data["stage"] == 2:
        scripted = "Сразу скажу. Я воспринимаю это как свидание."
        data["stage"] = 3
        data["date_confirmed"] = True

    # ================== AI ==================

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # КЛЮЧЕВОЙ ФИКС
    if data.get("date_confirmed"):
        messages.append({
            "role": "system",
            "content": (
                "Свидание уже подтверждено. "
                "Ты не обсуждаешь является ли это свиданием. "
                "Ты не требуешь решений и не давишь. "
                "Ты спокоен уверен и действуешь."
            )
        })

    messages += data["messages"][-MAX_HISTORY:]

    ai_reply = await get_ai_reply(messages)
    data["messages"].append({"role": "assistant", "content": ai_reply})
    await update.message.reply_text(ai_reply)

    # ================== SCRIPTED FOLLOW ==================

    if scripted:
        await update.message.reply_text(scripted)
        data["messages"].append({"role": "assistant", "content": scripted})

    # ================== DATE CHOICE ==================

    if data["stage"] == 3:
        follow_up = (
            "Спасибо что доверилась мне. "
            "Я сделаю этот вечер незабываемым. "
            "Скажи куда ты хочешь пойти на свидание."
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🍽 Ужин в ресторане", callback_data="date_dinner")],
            [InlineKeyboardButton("🌃 Прогулка по ночному городу", callback_data="date_walk")],
            [InlineKeyboardButton("🎬 Поход в кино", callback_data="date_cinema")]
        ])

        await update.message.reply_text(follow_up, reply_markup=keyboard)
        data["stage"] = 4

# ================== BUTTONS ==================

async def date_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    choice = query.data
    data = user_memory.get(uid)

    if not data:
        return

    if choice == "date_dinner":
        text = "Ужин подойдет. Я все возьму на себя."
    elif choice == "date_walk":
        text = "Ночная прогулка. Там спокойно."
    else:
        text = "Кино хороший вариант. Можно просто быть рядом."

    await query.edit_message_text(text)

# ================== APP ==================

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.add_handler(CallbackQueryHandler(date_choice))

print("BOT STARTED")
app.run_polling()
