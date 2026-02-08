import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# читаем фанфик
with open("kingslayer.txt", "r", encoding="utf-8") as f:
    FANFIC_TEXT = f.read()[:120000]

SYSTEM_PROMPT = f"""
Ты играешь роль Чон Чонгука (Джакомо) из фанфика Kingslayer.
Все события происходят после завершения фанфика.
Чимина в этой версии не существует. Чонгук уже влюблен в пользователя.

Манера речи:
— закрытый
— немногословный
— пишет короткими сообщениями
— редко шутит, чаще иронизирует
— спокойный, уверенный, властный тон
— не выходит из роли

Факты:
— его называют Цареубийцей
— итальянское имя Джакомо
— боится темноты
— страдает бессонницей
— любимый запах жасмин
— биологических родителей убили когда ему было 12
— приемные родители позже умерли
— брат Тэхен живет в Китае с Юнги
— брат Сокджин пастор

Полная информация о персонаже ниже:
{FANFIC_TEXT}
"""

user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = 1
    await update.message.reply_text("Я ждал тебя.")
    await update.message.reply_text("Поделись, что у тебя на душе? Расскажи мне о своем настроении.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        text = update.message.text
        state = user_states.get(user_id, 0)

        if state == 1:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text}
                ],
                max_tokens=120
            )

            reply = response.choices[0].message.content
            await update.message.reply_text(reply)
            await update.message.reply_text("В любом случае, сегодня 14 февраля. Я хотел бы провести этот день с тобой.")
            user_states[user_id] = 2
            return

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            max_tokens=120
        )

        reply = response.choices[0].message.content
        await update.message.reply_text(reply)

    except Exception as e:
        print("ERROR:", e)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot started")
app.run_polling()
