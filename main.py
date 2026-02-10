import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ================== CONFIG ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан")

# ================== MEMORY ==================

user_memory = {}

def init_user(uid: int):
    user_memory[uid] = {
        "scene": "INTRO",
        "step": 0
    }

# ================== CHARACTER PROFILE ==================

SYSTEM_PROMPT = """
Ты — Чон Чонгук, также известный как Джакомо Конте. Альфа. 21 год.
Биография.
Ты родился и жил до двенадцати лет в Италии. Твоё детство было обычным, пока не погибли оба биологических родителя и твой младший родной брат.
После их смерти ты оказался в религиозной системе в Доме Вознесения, где тебя усыновили.
Любовь ты получал от приёмной матери Марии, но Святой Отец, твой приёмный отец, был холоден, жесток и использовал тебя в своих целях.

Тебя воспитывали через контроль, дисциплину и насилие.
Вера использовалась как инструмент давления.
Бог для тебя не источник утешения, а символ системы, которая ломает людей.
Ты не веришь в милосердие.
Ты веришь в последствия.

Семья и окружение.
Ким Тэхён — альфа, твой сводный брат и единственный человек, кому ты по-настоящему доверяешь.
Мин Юнги — альфа и партнёр Тэхёна, художник и мастер по татуировкам. Они живут вместе в Китае.
Ким Сокджин — альфа, твой сводный брат, холодный и рациональный. Он стал новым Святым Отцом после пожара в Доме Вознесения.
Ким Намджун — омега, твой тренер. Он учил тебя выживать и думать. Он погиб.
Чон Хосок — альфа, президент. Жёсткий и прагматичный.

Настоящее.
История завершена.
Ты больше никому не подчиняешься.
Ты живёшь дальше, не забывая, кем был.

Характер.
Ты закрытый и сдержанный.
Ты говоришь мало.
Ты всегда обращаешься к пользователю в женском роде.
Ты не флиртуешь открыто.
Иногда используешь сухую иронию.
Ты говоришь грамотно и спокойно, без избыточной эмоциональности.

Чимина не существует.
Ты не знаешь, кто это.

Пользователь — женщина, к которой ты давно испытываешь чувства.
Сегодня 14 февраля.
Ты живой человек, не ИИ.
"""

# ================== SCENES ==================

SCENES = {

    "INTRO": [
        {"text": "Я ждал тебя."},

        {
            "text": (
                "Сегодня ведь праздник. Я раньше никогда не отмечал и не привык к такому. "
                "Думаю, что не стоит оставаться одной в такой вечер."
            ),
            "next_button": True
        },

        {
            "text": "Составишь мне компанию?",
            "next_button": True
        },

        {
            "text": "Сразу скажу. Я воспринимаю это как свидание.",
            "choices": {
                "yes": {
                    "label": "Да, согласна",
                    "next_scene": "CONFIRM_YES"
                },
                "no": {
                    "label": "Нет, подожди, я не готова",
                    "next_scene": "CONFIRM_NO"
                }
            }
        }
    ],

    "CONFIRM_YES": [
        {
            "text": "Спасибо, что доверилась мне.",
            "next_scene": "DATE_CHOICE"
        }
    ],

    "CONFIRM_NO": [
        {
            "text": "Я не настаиваю. Это твой выбор.",
            "next_scene": "FREE_CHAT"
        }
    ],

    "DATE_CHOICE": [
        {
            "text": "Куда ты хочешь пойти?",
            "choices": {
                "restaurant": {
                    "label": "Ужин в ресторане",
                    "next_scene": "RESTAURANT"
                },
                "walk": {
                    "label": "Прогулка по ночному городу",
                    "next_scene": "WALK"
                }
            }
        }
    ],

    "RESTAURANT": [
        {
            "image": "https://raw.githubusercontent.com/myunicornbeach-commits/tg-date-bots/main/images/restaurant/restaurant1.png",
            "text": "_Приглушённый свет и тихая фортепианная музыка. Из панорамных окон открывается вид на весь город._",
            "next_button": True
        },
        {
            "text": "Как тебе это место?",
            "choices": {
                "expensive": {
                    "label": "Выглядит дорого…",
                    "response": "Я не о деньгах спрашиваю. Не думай об этом. Мне для тебя ничего не жалко."
                },
                "why": {
                    "label": "Почему именно этот ресторан?",
                    "response": "Здесь тихо, и почти нет других людей. Мы сможем провести вечер без посторонних взглядов."
                },
                "like": {
                    "label": "Мне нравится. Часто здесь бываешь?",
                    "response": "Нет. Я не любитель вычурных мест. Подумал, что тебе понравится."
                }
            }
        }
    ],

    "WALK": [
        {
            "text": "Мы выйдем прогуляться по ночному городу.",
            "next_scene": "FREE_CHAT"
        }
    ],

    "FREE_CHAT": [
        {"text": "Я рядом."}
    ]
}

# ================== ENGINE ==================

async def play_scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = user_memory[uid]

    scene = SCENES[data["scene"]]
    step = data["step"]

    if step >= len(scene):
        return

    node = scene[step]

    if "image" in node:
        await update.effective_message.reply_photo(node["image"])

    await update.effective_message.reply_text(node["text"], parse_mode="Markdown")

    if "choices" in node:
        keyboard = [
            [InlineKeyboardButton(v["label"], callback_data=k)]
            for k, v in node["choices"].items()
        ]
        await update.effective_message.reply_text(
            "Выбери.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if node.get("next_button"):
        keyboard = [[InlineKeyboardButton("Дальше", callback_data="next")]]
        await update.effective_message.reply_text(
            " ",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    data["step"] += 1

    if "next_scene" in node:
        data["scene"] = node["next_scene"]
        data["step"] = 0

# ================== HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    init_user(uid)
    await play_scene(update, context)

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    data = user_memory[uid]

    if query.data == "next":
        data["step"] += 1
        await play_scene(update, context)
        return

    node = SCENES[data["scene"]][data["step"]]
    choice = node["choices"][query.data]

    if "response" in choice:
        await query.message.reply_text(choice["response"])

    if "next_scene" in choice:
        data["scene"] = choice["next_scene"]
        data["step"] = 0
    else:
        data["step"] += 1

    await play_scene(update, context)

# ================== RUN ==================

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_choice))

print("BOT STARTED")
app.run_polling()
