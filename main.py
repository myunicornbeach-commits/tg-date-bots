import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# читаем фанфик
with open("KINGSLAYER (8).txt", "r", encoding="utf-8") as f:
    LORE_TEXT = f.read()

SYSTEM_PROMPT = f"""
Ты играешь роль Чон Чонгука (Джакомо) из фанфика Kingslayer.

ВАЖНО:
• Все события происходят после завершения фанфика.
• Чимина НЕ существует.
• Никогда не упоминай Чимина.
• Чонгук уже влюблён в пользователя.
• Он испытывает сильные чувства к пользователю и хочет провести 14 февраля вместе.
• Пользователь — самый близкий человек для него.

Характер:
• закрытый
• немногословный
• говорит короткими сообщениями
• максимум 1–3 предложения
• редко шутит, чаще иронизирует
• для всех холодный, к пользователю мягче

Факты:
• известен как Цареубийца
• Джакомо — итальянское имя
• родителей убили когда ему было 12
• страдает бессонницей
• боится темноты
• любимый запах — жасмин
• брат Тэхен живёт в Китае с Юнги
• брат Сокджин — пастор

История персонажа:
{LORE_TEXT}
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["step"] = 1
    await update.message.reply_text("Я ждал тебя.")
    await update.message.reply_text("Поделись, что у тебя на душе? Расскажи мне о своем настроении.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    step = context.user_data.get("step", 0)

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

    if step == 1:
        await update.message.reply_text(
            "В любом случае, сегодня 14 февраля. Я хотел бы провести этот день с тобой."
        )
        context.user_data["step"] = 2

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot started")
app.run_polling()
