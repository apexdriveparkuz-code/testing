# bot.py
# Yandex Taxi operatorlari uchun kunlik hisobot boti
# Ishga tushirish: python bot.py

import logging
from datetime import date, timedelta, datetime, time as dtime
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import config
import database as db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ro'yxatdan o'tish jarayonidagi foydalanuvchilar: {chat_id: True}
awaiting_registration_code = {}
awaiting_name = {}

# Savol-javob jarayonidagi operatorlar:
# {chat_id: {"index": int, "answers": {}, "date": "YYYY-MM-DD"}}
pending_reports = {}


def is_admin(chat_id: int) -> bool:
    return chat_id == config.ADMIN_CHAT_ID


# ---------- Ro'yxatdan o'tish ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if is_admin(chat_id):
        await update.message.reply_text(
            "Salom! Siz admin sifatida ro'yxatdan o'tgansiz.\n\n"
            "Buyruqlar:\n"
            "/hisobot - bugungi hisobotni ko'rish\n"
            "/hisobot_hafta - so'nggi 7 kunlik hisobot\n"
            "/operatorlar - ro'yxatdagi operatorlar"
        )
        return

    if db.is_operator(chat_id):
        await update.message.reply_text(
            "Assalomu alaykum! Siz ro'yxatdan o'tgansiz.\n"
            "Kunlik hisobotingizni topshirish uchun /hisobot buyrug'ini yuboring."
        )
        return

    awaiting_registration_code[chat_id] = True
    await update.message.reply_text(
        "Assalomu alaykum! Bu bot orqali kunlik ish hisobotingizni topshirasiz.\n\n"
        "Ro'yxatdan o'tish uchun maxfiy kodni kiriting:"
    )


async def handle_registration_code(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str):
    if text.strip() == config.REGISTRATION_CODE:
        del awaiting_registration_code[chat_id]
        awaiting_name[chat_id] = True
        await update.message.reply_text("Kod to'g'ri ✅\nEndi ism-familiyangizni yozing:")
    else:
        await update.message.reply_text("Kod noto'g'ri. Qaytadan urinib ko'ring:")


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str):
    full_name = text.strip()
    db.add_operator(chat_id, full_name)
    del awaiting_name[chat_id]
    await update.message.reply_text(
        f"Rahmat, {full_name}! Siz operator sifatida ro'yxatga qo'shildingiz.\n\n"
        "Har kuni belgilangan vaqtda sizdan qisqa hisobot so'rayman. "
        "Xohlagan vaqtda o'zingiz ham /hisobot buyrug'i bilan topshirishingiz mumkin."
    )


# ---------- Kunlik savol-javob jarayoni ----------

async def begin_report_flow(chat_id: int, context: ContextTypes.DEFAULT_TYPE, report_date: str = None):
    if report_date is None:
        report_date = date.today().isoformat()
    pending_reports[chat_id] = {"index": 0, "answers": {}, "date": report_date}
    key, question = config.QUESTIONS[0]
    await context.bot.send_message(chat_id=chat_id, text=question)


async def ask_next_or_finish(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    state = pending_reports[chat_id]
    idx = state["index"]

    if idx >= len(config.QUESTIONS):
        db.save_report(chat_id, state["date"], state["answers"])
        del pending_reports[chat_id]
        await update.message.reply_text("Rahmat! Bugungi hisobotingiz saqlandi ✅")
        return

    key, question = config.QUESTIONS[idx]
    await update.message.reply_text(question)


async def handle_report_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str):
    state = pending_reports[chat_id]
    idx = state["index"]
    key, question = config.QUESTIONS[idx]

    # Raqam kutilyapti - tekshiramiz
    cleaned = text.strip()
    if not cleaned.lstrip("-").isdigit():
        await update.message.reply_text("Iltimos, faqat son kiriting (masalan: 3). Qaytadan:")
        return

    state["answers"][key] = int(cleaned)
    state["index"] += 1
    await ask_next_or_finish(update, context, chat_id)


async def cmd_hisobot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if is_admin(chat_id):
        await send_admin_report(context, date.today().isoformat())
        return

    if not db.is_operator(chat_id):
        await update.message.reply_text("Avval /start buyrug'i bilan ro'yxatdan o'ting.")
        return

    if chat_id in pending_reports:
        await update.message.reply_text("Siz allaqachon hisobot to'ldiryapsiz. Davom eting.")
        return

    await begin_report_flow(chat_id, context)


async def cmd_hisobot_hafta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_admin(chat_id):
        await update.message.reply_text("Bu buyruq faqat admin uchun.")
        return

    end = date.today()
    start_d = end - timedelta(days=6)
    rows = db.get_reports_for_range(start_d.isoformat(), end.isoformat())

    if not rows:
        await update.message.reply_text("So'nggi 7 kunda hisobot topilmadi.")
        return

    totals = {key: 0 for key, _ in config.QUESTIONS}
    per_operator = {}

    for op_chat_id, full_name, report_date, answers in rows:
        per_operator.setdefault(full_name, {key: 0 for key, _ in config.QUESTIONS})
        for key, val in answers.items():
            totals[key] = totals.get(key, 0) + val
            per_operator[full_name][key] += val

    lines = [f"📊 So'nggi 7 kunlik hisobot ({start_d.isoformat()} — {end.isoformat()})\n"]
    lines.append("Umumiy:")
    for key, question in config.QUESTIONS:
        lines.append(f"  {question} → {totals.get(key, 0)}")

    lines.append("\nOperatorlar bo'yicha:")
    for name, vals in per_operator.items():
        lines.append(f"\n👤 {name}")
        for key, question in config.QUESTIONS:
            lines.append(f"  {question} → {vals.get(key, 0)}")

    await update.message.reply_text("\n".join(lines))


async def cmd_operatorlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_admin(chat_id):
        await update.message.reply_text("Bu buyruq faqat admin uchun.")
        return

    ops = db.get_all_operators()
    if not ops:
        await update.message.reply_text("Hozircha operatorlar ro'yxatga olinmagan.")
        return

    lines = ["👥 Ro'yxatdagi operatorlar:\n"]
    for chat_id_op, name in ops:
        lines.append(f"- {name} (id: {chat_id_op})")
    await update.message.reply_text("\n".join(lines))


# ---------- Umumiy matn handler ----------

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    if chat_id in awaiting_registration_code:
        await handle_registration_code(update, context, chat_id, text)
        return

    if chat_id in awaiting_name:
        await handle_name(update, context, chat_id, text)
        return

    if chat_id in pending_reports:
        await handle_report_answer(update, context, chat_id, text)
        return

    await update.message.reply_text(
        "Buyruqni tushunmadim. /hisobot yozib hisobot topshirishingiz mumkin."
    )


# ---------- Avtomatik jadval bo'yicha vazifalar ----------

async def daily_question_job(context: ContextTypes.DEFAULT_TYPE):
    """Har kuni belgilangan vaqtda barcha operatorlarga savol yuboradi."""
    operators = db.get_all_operators()
    today = date.today().isoformat()
    for chat_id, name in operators:
        if chat_id in pending_reports:
            continue  # allaqachon jarayonda
        try:
            await begin_report_flow(chat_id, context, today)
        except Exception as e:
            logger.warning(f"Operatorga xabar yuborilmadi ({name}, {chat_id}): {e}")


async def send_admin_report(context: ContextTypes.DEFAULT_TYPE, report_date: str):
    if config.ADMIN_CHAT_ID == 0:
        logger.warning("ADMIN_CHAT_ID sozlanmagan, hisobot yuborilmadi.")
        return

    rows = db.get_reports_for_date(report_date)
    operators = db.get_all_operators()

    if not rows:
        await context.bot.send_message(
            chat_id=config.ADMIN_CHAT_ID,
            text=f"📊 {report_date} uchun hali hech kim hisobot topshirmagan.",
        )
        return

    reported_ids = {op_id for op_id, _, _ in rows}
    missing = [name for chat_id, name in operators if chat_id not in reported_ids]

    totals = {key: 0 for key, _ in config.QUESTIONS}
    lines = [f"📊 Kunlik hisobot — {report_date}\n"]

    for op_chat_id, full_name, answers in rows:
        lines.append(f"👤 {full_name}")
        for key, question in config.QUESTIONS:
            val = answers.get(key, 0)
            totals[key] += val
            lines.append(f"  {question} → {val}")
        lines.append("")

    lines.append("— — —")
    lines.append("Umumiy jami:")
    for key, question in config.QUESTIONS:
        lines.append(f"  {question} → {totals[key]}")

    if missing:
        lines.append("\n⚠️ Hisobot topshirmaganlar: " + ", ".join(missing))

    await context.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text="\n".join(lines))


async def daily_report_job(context: ContextTypes.DEFAULT_TYPE):
    await send_admin_report(context, date.today().isoformat())


# ---------- Ishga tushirish ----------

def main():
    db.init_db()

    app = Application.builder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hisobot", cmd_hisobot))
    app.add_handler(CommandHandler("hisobot_hafta", cmd_hisobot_hafta))
    app.add_handler(CommandHandler("operatorlar", cmd_operatorlar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    tz = ZoneInfo(config.TIMEZONE)
    job_queue = app.job_queue
    job_queue.run_daily(
        daily_question_job,
        time=dtime(config.DAILY_QUESTION_HOUR, config.DAILY_QUESTION_MINUTE, tzinfo=tz),
    )
    job_queue.run_daily(
        daily_report_job,
        time=dtime(config.DAILY_REPORT_HOUR, config.DAILY_REPORT_MINUTE, tzinfo=tz),
    )

    logger.info("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
