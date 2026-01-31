import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

HEADERS = {"User-Agent": "Mozilla/5.0"}

ADMIN_ID = 7979780050
USERS_FILE = "users.txt"
BANNED_FILE = "banned.txt"

TOKEN = os.getenv("BOT_TOKEN")

FOOTER = (
    "\n\n━━━━━━━━━━━━━━━\n"
    "👨‍💻 *Dasturchi:* @xyperh\n"
    "🚀 *Ushbu bot Amirxan Ashiraliyev tomonidan yaratilgan*"
)

# ========= USER SAVE =========
def save_user(user):
    uid = user.id
    uname = user.username or "no_username"
    line = f"{uid}|{uname}"

    try:
        with open(USERS_FILE, "a+") as f:
            f.seek(0)
            data = f.read().splitlines()
            ids = [x.split("|")[0] for x in data]

            if str(uid) not in ids:
                f.write(line + "\n")
    except:
        pass

def get_users():
    try:
        with open(USERS_FILE) as f:
            return f.read().splitlines()
    except:
        return []

# ========= BAN =========
def get_banned():
    try:
        with open(BANNED_FILE) as f:
            return f.read().splitlines()
    except:
        return []

def is_banned(uid):
    return str(uid) in get_banned()

def ban_user(uid):
    with open(BANNED_FILE, "a+") as f:
        f.seek(0)
        bans = f.read().splitlines()
        if str(uid) not in bans:
            f.write(str(uid) + "\n")

def unban_user(uid):
    bans = get_banned()
    if str(uid) in bans:
        bans.remove(str(uid))
        with open(BANNED_FILE, "w") as f:
            f.write("\n".join(bans))

# ========= ISM =========
def ism_manosi(ism):
    ism = ism.capitalize().strip()
    url = f"https://ismlar.com/name/{ism}"

    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        h1 = soup.find("h1")
        if not h1:
            return None

        p = h1.find_next("p")
        return p.get_text(strip=True) if p else None
    except:
        return None

# ========= START =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if is_banned(user.id):
        await update.message.reply_text(
            "🚫 *Siz ban qilingansiz!*\n\n"
            "Banni olish uchun murojaat qiling\n"
            "Admin: @xyperh",
            parse_mode="Markdown"
        )
        return

    save_user(user)

    await update.message.reply_text(
        "👋 *Salom!* Ism yuboring 😊" + FOOTER,
        parse_mode="Markdown"
    )

# ========= USERS LIST =========
async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    users = get_users()

    text = "👥 USERS LIST:\n\n"
    for i, u in enumerate(users, 1):
        uid, uname = u.split("|")
        text += f"{i}) @{uname} — {uid}\n"

    await update.message.reply_text(text)

# ========= BAN COMMANDS =========
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    uid = context.args[0]
    ban_user(uid)
    await update.message.reply_text("🚫 Ban qilindi")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    uid = context.args[0]
    unban_user(uid)
    await update.message.reply_text("✅ Unban qilindi")

# ========= MESSAGE =========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if is_banned(user.id):
        await update.message.reply_text(
            "🚫 *Siz ban qilingansiz!*\n"
            "Admin: @xyperh",
            parse_mode="Markdown"
        )
        return

    save_user(user)

    ism = update.message.text.strip()
    manosi = ism_manosi(ism)
    found = bool(manosi)

    # 🔔 ADMIN LOG
    admin_text = (
        "📥 *Yangi qidiruv*\n\n"
        f"👤 @{user.username or 'yo‘q'}\n"
        f"🆔 `{user.id}`\n"
        f"🔎 {ism}\n"
        f"📌 {'Topildi ✅' if found else 'Topilmadi ❌'}"
    )

    await context.bot.send_message(
        ADMIN_ID,
        admin_text,
        parse_mode="Markdown"
    )

    # USERGA JAVOB
    if manosi:
        msg = f"📝 *{ism}* ma'nosi:\n\n{manosi}"
    else:
        msg = "❌ Topilmadi"

    msg += FOOTER
    await update.message.reply_text(msg, parse_mode="Markdown")

# ========= MAIN =========
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("users", users_list))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
