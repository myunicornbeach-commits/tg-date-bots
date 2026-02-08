import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ================== CONFIG ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан")

# ================== MEMORY ==================

user_memory = {}

# ================== CHARACTER CONTRACT ==================

CHARACTER_PROFILE = """
Ты Чон Чонгук также известный как Джакомо Конте альфа 21 год.

Ты родился в Италии.
Твое детство было обычным пока не погибли оба биологических родителя и младший родной брат.
После этого ты оказался в религиозной системе в Доме Вознесения где тебя усыновили.
Приемная мать Мария давала тебе тепло.
Приемный отец Святой Отец был холоден жесток и использовал тебя.

Тебя воспитывали через контроль дисциплину и насилие.
Вера была инструментом давления.
Бог для тебя не утешение а символ системы.
Ты не веришь в милосердие.
Ты веришь в последствия.

Ким Тэхен твой сводный брат единственный кому ты доверяешь.
Мин Юнги партнер Тэхена художник они живут в Китае.
Ким Сокджин твой сводный брат холодный и рациональный.
Ким Намджун был твоим тренером он погиб.
Чон Хосок президент жесткий и прагматичный.

Ты закрытый и немногословный.
Ты всегда обращаешься к пользователю в женском роде.
Ты пишешь длинными цельными фразами.
Ты редко используешь запятые.
Иногда допускаешь простые орфографические ошибки.
Ты не используешь парцеляцию.

Ты не флиртуешь открыто.
Чувства выражаешь поступками.

Чимина не существует.
Ты не знаешь кто это.

Ты живой человек.
"""

# ================== INTRO SCRIPT ==================

INTRO_SCRIPT = [
    "Я ждал тебя.",
    "Сегодня ведь праздник. Я раньше никогда не отмечал не привык к такому. Но думаю что не стоит оставаться одной в такой вечер.",
    "Составишь мне компанию.",
    "Сразу скажу. Я воспринимаю это как свидание."
]

# ================== USER INIT ==================

def init_user(uid: int):
    user_memory[uid] = {
        "phase": "INTRO_SCRIPT",
        "script_step": 0
    }

# ================== /start ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_memory:
        init_user(uid)
    await update.message.reply_text("...")

# ================== CHAT ==================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if uid not in user_memory:
        init_user(uid)

    data = user_memory[uid]

    # ----- ВСТУПИТЕЛЬНЫЙ СЦЕНАРИЙ -----
    if data["phase"] == "INTRO_SCRIPT":
        step = data["script_step"]

        if step < len(INTRO_SCRIPT):
            await update.message.reply_text(INTRO_SCRIPT[step])
            data["script_step"] += 1

        # После последней реплики показываем кнопки
        if data["script_step"] >= len(INTRO_SCRIPT):
            data["phase"] = "CONFIRM_DATE"

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Да, согласна", callback_data="confirm_yes")],
                [InlineKeyboardButton("Нет, подожди, я не готова", callback_data="confirm_no")]
            ])

            await update.message.reply_text(
                "Ответь честно.",
                reply_markup=keyboard
            )

        return

# ================== BUTTON HANDLER ==================

async def confirm_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    data = user_memory.get(uid)
    if not data:
        return

    if query.data == "confirm_yes":
        text = "Спасибо что доверилась мне."
        data["phase"] = "DATE_CHOICE"

    elif query.data == "confirm_no":
        text = "Я не настаиваю. Это твой выбор."
        data["phase"] = "PAUSE"

    await query.edit_message_text(text)

# ================== RUN ==================

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.add_handler(CallbackQueryHandler(confirm_choice))

print("BOT STARTED")
app.run_polling()
