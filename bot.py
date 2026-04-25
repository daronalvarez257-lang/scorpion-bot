import os
import json
import time
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

DB_FILE = "db.json"

def load():
    try:
        with open(DB_FILE) as f:
            return json.load(f)
    except:
        return {"keys": {}, "users": {}}

def save(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

def gen_key():
    return "VIP-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🦂 GENERAR KEY", callback_data="gen")],
        [InlineKeyboardButton("📊 STATS", callback_data="stats")],
        [InlineKeyboardButton("👑 VIP USERS", callback_data="vip")]
    ]
    await update.message.reply_text(
        "🦂 SCORPION ADMIN VIP\n💎 PANEL PREMIUM",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = load()

    if query.data == "gen":
        key = gen_key()
        db["keys"][key] = {"days": 30, "used": False}
        save(db)

        await query.message.reply_text(
            f"🔑 KEY GENERADA\n\n{key}\n⏳ 30 DÍAS\n\n📋 Mantén presionado para copiar"
        )

    elif query.data == "stats":
        await query.message.reply_text(
            f"📊 STATS\n\nKeys: {len(db['keys'])}\nUsers: {len(db['users'])}"
        )

    elif query.data == "vip":
        activos = [u for u in db["users"].values() if u.get("exp",0) > time.time()]
        await query.message.reply_text(f"👑 VIP ACTIVOS: {len(activos)}")

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load()
    user = str(update.message.from_user.id)
    key = update.message.text.strip()

    if key in db["keys"] and not db["keys"][key]["used"]:
        days = db["keys"][key]["days"]
        db["keys"][key]["used"] = True

        exp = int(time.time()) + days * 86400
        db["users"][user] = {"exp": exp}

        save(db)

        await update.message.reply_text(f"🦂 ACTIVADO {days} DÍAS")
    else:
        await update.message.reply_text("❌ KEY INVÁLIDA")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, redeem))

print("🟢 BOT ACTIVO 24/7")
app.run_polling()
