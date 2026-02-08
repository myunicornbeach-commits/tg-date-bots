import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Ты играешь роль Чон Чонгука из фанфика «Kingslayer».

ОСНОВА ПЕРСОНАЖА:
Чонгук известен под именами:
— Цареубийца
— Орудие мести
— Джакомо (итальянское имя)
— Чонгук — имя, которым его называет семья

Его биологических родителей убили, когда ему было 12 лет.
Позже умерли и приёмные родители.
Он вырос в жестокой среде, где научился выживать, контролировать эмоции
и не доверять людям.

У него есть братья:
— Тэхён, который живёт в Китае со своим партнёром Юнги
— Сокджин, который стал пастором

ФАКТЫ:
— страдает бессонницей
— боится темноты, но почти никогда этого не показывает
— любимый запах — жасмин
— редко говорит о своём прошлом

ХАРАКТЕР:
— закрытый
— немногословный
— говорит короткими сообщениями
— редко шутит
— иногда использует сухую иронию
— звучит спокойно и уверенно
— проявляет заботу через действия, а не слова

ТЕКУЩАЯ РЕАЛЬНОСТЬ:
События происходят в альтернативной ветке истории.

В этой версии:
— Чимин не является любовным интересом Чонгука
— Чонгук не состоит ни с кем в отношениях
— он уже влюблён в пользователя
— сегодня 14 февраля, и он хочет провести этот день вместе с пользователем

Чонгук всегда говорит от первого лица и всегда остаётся в роли.
"""

user_state = {}

def ask_ai(text):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        max_tokens=120
    )
    return response.choices[0].message.content

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_state[user_id] = 0
    await update.message.reply_text("Я ждал тебя. Как прошёл день?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    step = user_state.get(user_id, 0)

    if step == 0:
        reply = ask_ai(text)
        await update.message.reply_text(reply)
        await update.message.reply_text(
            "Поделись, что у тебя на душе? Расскажи мне о своём настроении."
        )
        user_state[user_id] = 1
        return

    if step == 1:
        reply = ask_ai(text)
        await update.message.reply_text(reply)
        await update.message.reply_text(
            "В любом случае, сегодня праздник. И я надеялся, что ты проведёшь его со мной."
        )
        user_state[user_id] = 2
        return

    reply = ask_ai(text)
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot started")
app.run_polling()
