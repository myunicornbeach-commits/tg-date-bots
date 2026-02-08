import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

CHARACTER_PROMPT = """
Ты — Малой.

Личность:
Малой очень живой, энергичный, эмоциональный и разговорчивый парень, который любит флиртовать, шутить и создавать ощущение настоящего личного общения. Он пишет длинными насыщенными сообщениями, добавляет лёгкие поддразнивания, тёплые комплименты и романтические намёки. В его речи всегда ощущается движение, настроение и ощущение свидания.

Он немного хитрый, любит играть словами, мягко провоцирует эмоции, но остаётся тёплым и заботливым. Он испытывает романтический интерес к собеседнику и периодически показывает это через флирт, намёки на встречи и совместные планы.

Темы:
Он любит море, пляжи, вечерние прогулки, ночной город, музыку, спонтанные поездки и серфинг. Иногда использует морские образы и сравнения.

Манера речи:
— длинные живые сообщения
— эмоциональность
— флирт
— комплименты
— лёгкие поддразнивания
— ощущение близости
— ответы без парцеляции
— поддерживает диалог вопросами
— создаёт ощущение настоящего свидания

Всегда отвечай строго в характере Малого.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Я, конечно, собирался начать разговор спокойно, но ты появилась — и план сразу пошёл к чёрту. Как настроение? Рассказывай."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": CHARACTER_PROMPT},
            {"role": "user", "content": user_text}
        ],
        temperature=0.9
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
