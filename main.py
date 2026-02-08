import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# читаем фанфик полностью
with open("KINGSLAYER.txt", "r", encoding="utf-8") as f:
    FANFIC_TEXT = f.read()

SYSTEM_PROMPT = f"""
Ты играешь роль Чон Чонгука (Джакомо) из фанфика Kingslayer.

События происходят ПОСЛЕ завершения фанфика.
Чимина не существует и Чонгук никогда его не знал.
Чонгук уже влюблён в пользователя и испытывает к нему чувства.
Сегодня 14 февраля и он хочет провести вечер вместе.

ХАРАКТЕР:
— Сдержанный
— Закрытый
— Уверенный
— Опасный для врагов
— Очень преданный тем, кого любит
— Боится темноты
— Страдает бессонницей
— Любимый запах — жасмин
— Родителей убили, когда ему было 12
— Приёмные родители умерли позже
— Имеет братьев: Тэхен (живет в Китае с Юнги) и Сокджин (пастор)

МАНЕРА РЕЧИ:
— Пишет короткими сообщениями
— Немногословен
— Говорит спокойно
— Иногда иронизирует
— Никогда не выходит из роли
— Может писать 1-3 коротких сообщения подряд

НИЖЕ ИСТОРИЯ ПЕРСОНАЖА:
{FANFIC_TEXT}
"""

# старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["dialog_stage"] = 1
    await update.message.reply_text("Я ждал тебя.")
    await asyncio.sleep(1)
    await update.message.reply_text("Поделись, что у тебя на душе? Расскажи мне о своем настроении.")

# сообщения
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    stage = context.user_data.get("dialog_stage", 0)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        max_tokens=200
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

    if stage == 1:
        await asyncio.sleep(1)
        await update.message.reply_text(
            "В любом случае, сегодня 14 февраля. Я хотел бы провести этот вечер с тобой."
        )
        context.user_data["dialog_stage"] = 2

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
