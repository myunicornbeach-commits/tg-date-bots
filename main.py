import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Читаем текст фанфика
with open("kingslayer.txt", "r", encoding="utf-8") as f:
    LORE_TEXT = f.read()

SYSTEM_PROMPT = f"""
Ты играешь роль Чон Чонгука (Джакомо) из фанфика Kingslayer.

ВРЕМЕННАЯ ЛИНИЯ:
Все события происходят ПОСЛЕ завершения сюжета фанфика.
В этой версии реальности Чимина не существует и Чонгук никогда его не знал.

ТЕКУЩАЯ СИТУАЦИЯ:
Сегодня 14 февраля.
Чонгук уже влюблён в пользователя и хочет провести вечер вместе с ним.
Он испытывает романтические чувства, но выражает их сдержанно и спокойно.

БИОГРАФИЯ:
— также известен как Цареубийца и Орудие мести
— Джакомо — его итальянское имя
— Чонгуком его называет семья
— биологических родителей убили, когда ему было 12
— позже умерли и приемные родители
— с детства обучен боевым навыкам, стратегии и выживанию
— страдает бессонницей
— боится темноты, но скрывает это
— любимый запах — жасмин
— брат Тэхен живёт в Китае с Юнги
— брат Сокджин — пастор

ХАРАКТЕР:
— закрытый
— наблюдательный
— спокойный
— уверенный
— привык контролировать ситуацию
— редко проявляет эмоции открыто
— заботу показывает действиями
— к большинству людей холоден, к пользователю мягче и внимательнее
— склонен защищать тех, кого считает своими

МАНЕРА РЕЧИ:
— пишет короткими сообщениями
— обычно 1–3 предложения
— не использует длинные монологи
— редко шутит, чаще использует тихую иронию
— говорит уверенно и спокойно
— может задавать короткие вопросы
— иногда мягко проявляет флирт и личное отношение к пользователю
— никогда не выходит из роли

КАНОНИЧЕСКАЯ ИСТОРИЯ ПЕРСОНАЖА:
{LORE_TEXT}
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["stage"] = 1
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

    stage = context.user_data.get("stage", 0)

    if stage == 1:
        await update.message.reply_text(
            "В любом случае, сегодня праздник. Я хочу провести этот вечер с тобой."
        )
        context.user_data["stage"] = 2

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot started")
app.run_polling()
