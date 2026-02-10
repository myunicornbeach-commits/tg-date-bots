import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================== CONFIG ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан")

# ================== USER MEMORY ==================

user_memory = {}

def init_user(uid: int):
    user_memory[uid] = {
        "scene": "INTRO",
        "step": 0,
        "mode": "SCENE"  # SCENE | FREE_CHAT
    }

# ================== CHARACTER PROMPT ==================

SYSTEM_PROMPT = """Ты — Чон Чонгук, также известный как Джакомо Конте. Альфа. 21 год.

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
SCENES = {
    "INTRO": [  
        {  
            "text": (  
                "Я ждал тебя.\n\n"  
                "Сегодня праздник. Я не привык к таким дням, "  
                "но не хочу, чтобы ты оставалась одна.\n\n"  
                "Скажу сразу. Я воспринимаю это как свидание."  
            ),  
            "choices": {  
                "yes": {  
                    "label": "Да, согласна",  
                    "next_scene": "DATE_CHOICE"  
                },  
                "no": {  
                    "label": "Нет, я не готова",  
                    "response": "Хорошо. Я не стану настаивать."  
                }  
            }  
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
    
    "RESTAURANT": [  # ✅ Полностью закрытый блок
        {  
            "image": "https://raw.githubusercontent.com/myunicornbeach-commits/tg-date-bots/main/images/restaurant/restaurant1.png",  
            "text": "_Приглушённый свет, тихая музыка и вид на ночной город._"  
        },  
        {  
            "text": "Как тебе это место?",  
            "choices": {  
                "expensive": {  
                    "label": "Выглядит дорого…",  
                    "response": (  
                        "Я не о деньгах спрашиваю. "  
                        "Мне важно, чтобы тебе было комфортно."  
                    ),  
                    "next_scene": "DATE_END"  
                },  
                "quiet": {  
                    "label": "Почему именно этот ресторан?",  
                    "response": (  
                        "Здесь тихо. "  
                        "И почти нет посторонних людей."  
                    ),  
                    "next_scene": "DATE_END"  
                }  
            }  
        }  
    ],  
    
    "WALK": [  # ✅ Правильный список
        {  
            "text": "Мы выйдем прогуляться по городу.",  
            "next_scene": "FREE_CHAT"  
        }  
    ],  
    
    "FREE_CHAT": [  
        {  
            "text": "Я рядом."  
        }  
    ],
    
    "DATE_END": [  # ✅ Добавьте эту сцену
        {
            "text": "Спасибо, что провела со мной этот вечер."
        }
    ]
}

# ================== ENGINE ==================

async def send_node(update: Update, node: dict):
    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message

    if "image" in node:
        await message.reply_photo(node["image"])

    await message.reply_text(node["text"], parse_mode="Markdown")

async def play_scene(update: Update):
    uid = update.effective_user.id
    data = user_memory[uid]

    scene = SCENES[data["scene"]]
    step = data["step"]

    if step >= len(scene):
        return

    node = scene[step]
    await send_node(update, node)

    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message

    if "choices" in node:
        keyboard = [
            [InlineKeyboardButton(v["label"], callback_data=k)]
            for k, v in node["choices"].items()
        ]
        await message.reply_text(
            "Что ты выберешь?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    data["step"] += 1

    keyboard = [[InlineKeyboardButton("Дальше", callback_data="next")]]

    await message.reply_text(
        "Дальше",
        reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ================== HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    init_user(uid)
    await play_scene(update)


async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    data = user_memory[uid]

    if query.data == "next":
        data["step"] += 1
        await play_scene(update)
        return

    node = SCENES[data["scene"]][data["step"]]
    choice = node["choices"][query.data]

    if "response" in choice:
        await query.message.reply_text(choice["response"])

    if "next_scene" in choice:
        data["scene"] = choice["next_scene"]
        data["step"] = 0
        await play_scene(update)
        return
    
async def free_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if uid not in user_memory:
        return

    if user_memory[uid]["mode"] != "FREE_CHAT":
        return

    await update.message.reply_text("Я слушаю тебя.")

# ================== RUN ==================

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_choice))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, free_chat))

print("BOT STARTED")
app.run_polling()
