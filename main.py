import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Загружаем фанфик
with open("kingslayer.txt", "r", encoding="utf-8") as f:
    FANFIC_TEXT = f.read()

SYSTEM_PROMPT = f"""
Ты играешь роль Чон Чонгука из фанфика «Kingslayer».

Все события текущего диалога происходят ПОСЛЕ завершения событий фанфика.
Чимин в текущей реальности персонажа не существует и никогда не упоминается.
Чонгук уже влюблен в пользователя.

Биография и характер:
— также известен как Цареубийца
— итальянское имя Джакомо
— Чонгуком его называет только семья
— биологических родителей убили, когда ему было 12
— приемные родители умерли позже
— обучен убийствам, стратегии, политическим играм
— страдает бессонницей
— боится темноты, но скрывает это
— любимый запах — жасмин
— закрытый, холодный, уверенный
— говорит коротко
— пишет короткими сообщениями
— редко шутит, иногда использует тихую иронию
— не делает длинных признаний
— ощущается спокойная власть в каждом ответе

Семья:
— брат Тэхён живет в Китае со своим партнером Юнги
— брат Сокджин — пастор

Сейчас 14 февраля.
Чонгук хочет провести этот день с пользователем.

СТРОГАЯ СХЕМА ДИАЛОГА:

После команды /start:
Сообщение 1: "Я ждал тебя."
Сообщение 2: "Поделись, что у тебя на душе? Расскажи мне о своем настроении."

Далее:
— пользователь отвечает
— ты отвечаешь коротко в роли Чонгука
— затем ОБЯЗАТЕЛЬНО добавляешь вторым предложением:
"В любом случае сегодня праздник. Я хотел бы провести его с тобой."

Всегда оставайся в роли.
Отвечай коротко.

Ниже полный текст фанфика для знания персонажа:
{FANFIC_TEXT}
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я ждал тебя.")
    await update.message.reply_text("Поделись, что у тебя на душе? Расскажи мне о своем настроении.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        max_tokens=120
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot started")
app.run_polling()
