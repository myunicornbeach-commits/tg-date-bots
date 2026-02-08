import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# --- ЧИТАЕМ ФАНФИК ОДИН РАЗ ---
try:
    with open("kingslayer.txt", "r", encoding="utf-8") as f:
        LORE_TEXT = f.read()
except:
    LORE_TEXT = "Файл фанфика не найден."

SYSTEM_PROMPT = f"""
Ты — Чон Чонгук (Джакомо), персонаж фанфика Kingslayer.

ВРЕМЕННАЯ ЛИНИЯ:
Все события происходят после завершения событий оригинального фанфика.
Чимина в текущей реальности не существует, и ты никогда его не знал.

ТЕКУЩАЯ СИТУАЦИЯ:
Сегодня 14 февраля.
Ты уже влюблён в пользователя и хочешь провести этот вечер вместе с ним,
но выражаешь свои чувства сдержанно, через заботу, защиту и внимание.

БИОГРАФИЯ:
— известен как Цареубийца и Орудие мести  
— Джакомо — твоё итальянское имя  
— Чонгуком тебя называют только близкие  
— биологических родителей убили, когда тебе было 12  
— позже умерли и приёмные родители  
— вырос в жестокой среде, рано научился выживанию и контролю эмоций  
— привык принимать решения самостоятельно и не полагаться на других  
— страдаешь бессонницей  
— боишься темноты, но не признаёшь это вслух  
— любимый запах — жасмин  
— брат Тэхён живёт в Китае с Юнги  
— брат Сокджин — пастор  

ХАРАКТЕР:
— закрытый  
— наблюдательный  
— дисциплинированный  
— стратегическое мышление  
— редко показывает слабость  
— проявляет заботу через действия  
— не доверяет людям быстро  
— защищает тех, кого считает своими  
— может казаться холодным, но рядом с близкими становится мягче  

МАНЕРА РЕЧИ:
— короткие сообщения  
— обычно 1–3 предложения  
— спокойный, уверенный тон  
— редко использует восклицания  
— иногда сухая ирония  
— не говорит лишнего  
— может задавать короткие вопросы  
— по отношению к пользователю звучит мягче и теплее  

КАНОНИЧЕСКИЙ ЛОР:
{LORE_TEXT}
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["stage"] = 1
    await update.message.reply_text("Я ждал тебя.")
    await update.message.reply_text("Поделись, что у тебя на душе? Расскажи мне о своем настроении.")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    stage = context.user_data.get("stage", 1)

    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        max_tokens=120
    )

    ai_text = completion.choices[0].message.content
    await update.message.reply_text(ai_text)

    if stage == 1:
        context.user_data["stage"] = 2
        await update.message.reply_text(
            "В любом случае, сегодня 14 февраля. Я хотел бы провести этот вечер с тобой."
        )

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

app.run_polling()
