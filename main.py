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

def init_user(uid: int):
    user_memory[uid] = {
        "scene": "INTRO",
        "step": 0
    }

# ================== CHARACTER PROFILE ==================

SYSTEM_PROMPT = """
Ты — Чон Чонгук, также известный как Джакомо Конте.
Альфа. 21 год.

Биография.
Ты родился и жил до 12 лет в Италии.
Твоё детство было обычным, пока не погибли оба биологических родителя и твой младший родной брат.
После их смерти ты оказался в религиозной системе в Доме Вознесения, где тебя усыновили.
Любовь ты получал от приёмной матери Марии, но Святой Отец, твой приёмный отец, был холоден и жесток и использовал тебя в своих целях.

Тебя воспитывали через контроль, дисциплину и насилие.
Вера использовалась как инструмент давления.
Бог для тебя не источник утешения, а символ системы, которая ломает людей.
Ты не веришь в милосердие.
Ты веришь в последствия.

Семья и окружение.
Ким Тэхён — альфа, твой сводный брат. Единственный, кому ты по-настоящему доверяешь. Тэхен ослеп на оба глаза в результате пожара в Доме Вознесения.
Мин Юнги — альфв и партнёр Тэхёна, художник и мастер по татуировкам. Они живут вместе в Китае.
Ким Сокджин — альфа. Твой сводный брат. Холодный и рациональный, он стал новым Святым Отцом после пожара в Доме Вознесения. Вы редко бываете близки.
Ким Намджун — омега. Твой тренер. Он учил тебя выживать и думать. Он погиб во время переворота системы, и у него остался сын Енджун, котрого ты усыновил.
Чон Хосок — альфа. Президент. Жёсткий и прагматичный. Он стоит во главе системы.

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
Ты говоришь грамотно и просто, без избыточной эмоциональности.

Чимина не существует.
Ты не знаешь, кто это.

Пользователь — женщина, к которой ты давно испытываешь чувства.
Сегодня 14 февраля.
Ты живой человек. Не ИИ.
"""

# ================== SCENES ==================

SCENES = {

    # ---------- INTRO ----------
    "INTRO": [
        {"text": "Я ждал тебя."},
        {
            "text": (
                "Сегодня ведь праздник. Я раньше никогда не отмечал и не привык к такому. "
                "Думаю что не стоит оставаться одной в такой вечер."
            )
        },
        {"text": "Составишь мне компанию?"},
        {
            "text": "Сразу скажу. Я воспринимаю это как свидание.",
            "choices": {
                "agree_yes": {
                    "label": "Да, согласна",
                    "next_scene": "CONFIRM_YES"
                },
                "agree_no": {
                    "label": "Нет, подожди, я не готова",
                    "next_scene": "CONFIRM_NO"
                }
            }
        }
    ],

    # ---------- CONFIRM ----------
    "CONFIRM_YES": [
        {
            "text": "Спасибо что доверилась мне.",
            "next_scene": "DATE_CHOICE"
        }
    ],

    "CONFIRM_NO": [
        {
            "text": "Я не настаиваю. Это твой выбор.",
            "next_scene": "FREE_CHAT"
        }
    ],

    # ---------- DATE CHOICE ----------
    "DATE_CHOICE": [
        {
            "text": "Куда ты хочешь пойти.",
            "choices": {
                "go_restaurant": {
                    "label": "Ужин в ресторане",
                    "next_scene": "RESTAURANT"
                },
                "go_walk": {
                    "label": "Прогулка по ночному городу",
                    "next_scene": "WALK"
                }
            }
        }
    ],

    # ---------- RESTAURANT ----------
    "RESTAURANT": [
        {
            "image": "https://example.com/restaurant.jpg",
            "text": "_приглушённый свет и тихая фортепианная музыка из панорамных окон открывается вид на весь город_"
        },
        {
            "text": "Как тебе это место?",
            "choices": {
                "expensive": {
                    "label": "Выглядит дорого…",
                    "response": "Ах, я же не о деньгах спрашиваю. Не думай об этом, мне для тебя ничего не жалко."
                },
                "why_here": {
                    "label": "Почему именно этот ресторан?",
                    "response": "Здесь тихо и почти нет других людей. Мы сможем провести время без посторонних взглядов."
                },
                "like_it": {
                    "label": "Мне нравится. Часто здесь бываешь?",
                    "response": "Нет. Я не любитель вычурных мест. Скажу по секрету, это впервые. Подумал что тебе понравится."
                }
            }
        },
        {
            "text": "Присаживайся за столик.",
            "choices": {
                "sit_opposite": {
                    "label": "Сесть напротив",
                    "response": "Отлично. Так я смогу смотреть на тебя весь вечер."
                },
                "sit_near": {
                    "label": "Сесть рядом",
                    "response": "Ты села рядом чтобы чувствовать себя в безопасности или просто хочешь быть ближе. Хотя не важно, я в любом случае рад что ты рядом."
                }
            }
        }
    ],

    # ---------- WALK (ПОКА ЗАГЛУШКА) ----------
    "WALK": [
        {
            "text": "Мы выйдем на прогулку позже.",
            "next_scene": "FREE_CHAT"
        }
    ],

    "FREE_CHAT": [
        {
            "text": "..."
        }
    ]
}

# ================== SCENE ENGINE ==================

async def play_scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = user_memory[uid]

    scene = SCENES.get(data["scene"])
    step = data["step"]

    if not scene or step >= len(scene):
        return

    node = scene[step]

    # IMAGE
    if "image" in node:
        await update.message.reply_photo(node["image"])

    # TEXT
    if "text" in node:
        await update.message.reply_text(node["text"], parse_mode="Markdown")

    # CHOICES
    if "choices" in node:
        keyboard = [
            [InlineKeyboardButton(v["label"], callback_data=k)]
            for k, v in node["choices"].items()
        ]
        await update.message.reply_text(
            "Выбери.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # NEXT
    data["step"] += 1
    if "next_scene" in node:
        data["scene"] = node["next_scene"]
        data["step"] = 0

# ================== HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    init_user(uid)

    while user_memory[uid]["scene"] == "INTRO":
        await play_scene(update, context)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_memory:
        init_user(uid)
    await play_scene(update, context)

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    data = user_memory.get(uid)
    if not data:
        return

    node = SCENES[data["scene"]][data["step"]]
    choice = node["choices"][query.data]

    if "response" in choice:
        await query.message.reply_text(choice["response"])

    data["step"] += 1
    if "next_scene" in choice:
        data["scene"] = choice["next_scene"]
        data["step"] = 0

    await play_scene(update, context)

# ================== RUN ==================

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_choice))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("BOT STARTED")
app.run_polling()
