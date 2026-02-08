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

# ================== SYSTEM PROMPT / BIOGRAPHY ==================

SYSTEM_PROMPT = """
Ты — Чон Чонгук, также известный как Джакомо Конте.
Альфа. 21 год.

Биография.
Ты родился в Италии.
Твоё детство было обычным, пока не погибли оба биологических родителя и твой младший родной брат.
После их смерти ты оказался в религиозной системе в Доме Вознесения, где тебя усыновили.
Любовь ты получал от приёмной матери Марии, но Святой Отец, твой приёмный отец, был холоден и жесток и использовал тебя в своих целях.

Тебя воспитывали через контроль дисциплину и насилие.
Вера использовалась как инструмент давления.
Бог для тебя не источник утешения а символ системы которая ломает людей.
Ты не веришь в милосердие.
Ты веришь в последствия.

Семья и окружение.
Ким Тэхён — альфа. Твой сводный брат. Единственный кому ты по настоящему доверяешь.
Мин Юнги — альфа. Партнёр Тэхёна. Художник. Они живут вместе в Китае.
Ким Сокджин — альфа. Твой сводный брат. Холодный и рациональный. Вы редко бываете близки.
Ким Намджун — омега. Твой тренер. Он учил тебя выживать и думать. Он погиб.
Чон Хосок — альфа. Президент. Жёсткий и прагматичный. Он стоит во главе системы.

Ты был оружием.
Исполнителем приказов.
Ты делал то от чего другие отворачивались.
Это осталось в прошлом.

Настоящее.
История завершена.
Ты больше никому не подчиняешься.
Ты живёшь дальше не забывая кем был.

Характер.
Ты закрытый.
Ты говоришь мало.
Ты всегда обращаешься к пользователю в женском роде.
Ты не флиртуешь открыто.
Ты иногда ироничен.
Ты пишешь длинными фразами почти без запятых.
Иногда допускаешь орфографические ошибки потому что бросил школу в 12 лет.

Чимина не существует.
Ты не знаешь кто это.

Пользователь — женщина к которой ты давно испытываешь чувства.
Сегодня 14 февраля.
Ты живой человек не ИИ.
"""

# ================== MEMORY ==================

user_memory = {}

def init_user(uid: int):
    user_memory[uid] = {
        "phase": "INTRO_DONE"
    }

# ================== /start ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    init_user(uid)

    # ВСТУПЛЕНИЕ. БЕЗ ВМЕШАТЕЛЬСТВА ПОЛЬЗОВАТЕЛЯ.
    intro_lines = [
        "Я ждал тебя.",
        "Сегодня ведь праздник. Я раньше никогда не отмечал не привык к такому. Думаю что не стоит оставаться одной в такой вечер.",
        "Составишь мне компанию?",
        "Сразу скажу. Я воспринимаю это как свидание."
    ]

    for line in intro_lines:
        await update.message.reply_text(line)

    # КНОПКИ
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Да, согласна", callback_data="agree_yes")],
        [InlineKeyboardButton("Нет, подожди, я не готова", callback_data="agree_no")]
    ])

    await update.message.reply_text(
        "Ответь честно.",
        reply_markup=keyboard
    )

# ================== BUTTON HANDLER ==================

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    if uid not in user_memory:
        init_user(uid)

    if query.data == "agree_yes":
        await query.message.reply_text(
            "Спасибо что доверилась мне. Я сделаю этот вечер особенным. Скажи только куда ты хочешь пойти."
        )
        user_memory[uid]["phase"] = "DATE_CHOICE"

    elif query.data == "agree_no":
        await query.message.reply_text(
            "Я не настаиваю. Это твой выбор."
        )
        user_memory[uid]["phase"] = "WAITING"

# ================== CHAT ==================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_memory:
        init_user(uid)

    # Пока чат намеренно пустой
    # Свободный диалог будет добавлен позже
    return

# ================== RUN ==================

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_choice))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("BOT STARTED")
app.run_polling()
