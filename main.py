import os
import json
import random
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler

# === CONFIGURATION ===
TOKEN = os.getenv("BOT_TOKEN")  # Use Railway environment variable
ADMIN_ID = 7693083453
KEYS_FILE = "keys.json"
DATABASE_FILES = ["logs.txt", "v2.txt", "v3.txt", "v4.txt", "v5.txt"]
USED_ACCOUNTS_FILE = "used_accounts.txt"
LINES_TO_SEND = 100

# === DOMAIN LIST ===
DOMAINS = [
    "100082", "authgop", "mtacc", "garena", "roblox", "gaslite", 
    "mobilelegends", "pubg", "codashop", "facebook", "Instagram", 
    "netflix", "tiktok", "telegram", "freefire", "bloodstrike"
]

# === LOAD DATABASE ===
if not os.path.exists(USED_ACCOUNTS_FILE):
    open(USED_ACCOUNTS_FILE, "w").close()

def load_keys():
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"keys": {}, "user_keys": {}, "logs": {}}
    return {"keys": {}, "user_keys": {}, "logs": {}}

def save_keys(data):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

keys_data = load_keys()

# === GENERATE KEY SYSTEM ===
def generate_random_key(length=5):
    return "NAME-" + ''.join(random.choices("0123456789", k=length))

def get_expiry_time(duration):
    now = datetime.now()
    duration_map = {
        "1m": 60, "5m": 300, "1h": 3600, "1d": 86400,
        "3d": 259200, "7d": 604800, "15d": 1296000, "30d": 2592000
    }
    return None if duration == "lifetime" else (now + timedelta(seconds=duration_map[duration])).timestamp()

# === START HANDLER ===
async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🔑 Get Premium Key", callback_data="get_key")],
        [InlineKeyboardButton("🛠 Generate Accounts", callback_data="generate_menu")],
        [InlineKeyboardButton("📊 Account Stats", callback_data="stats")],
        [InlineKeyboardButton("ℹ Bot Info", callback_data="info")]
    ]
    welcome_text = """
🌟 *Welcome to PREMIUM Account Generator Bot* 🌟

🔥 *Features:*
- Instant Account Generation
- Multiple Domains Supported
- Premium Quality Accounts
- Fast Delivery System

Use the buttons below to navigate:
"""
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def bot_info(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    info_text = """
🤖 *Bot Information*

🔹 *Version:* 2.0 Premium
🔹 *Developer:* @YourUsername
🔹 *Uptime:* 99.9%
🔹 *Accounts Generated:* 10,000+
🔹 *Last Update:* 2024-01-15
"""
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]]
    await query.edit_message_text(info_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def account_stats(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    try:
        with open(USED_ACCOUNTS_FILE, "r", encoding="utf-8", errors="ignore") as f:
            used_count = len(f.read().splitlines())
    except:
        used_count = 0

    stats_text = f"""
📊 *Account Statistics*

🔹 *Total Accounts Used:* {used_count}
🔹 *Available Domains:* {len(DOMAINS)}
🔹 *Database Files:* {len(DATABASE_FILES)}
🔹 *Daily Limit:* {LINES_TO_SEND} accounts/day

🔄 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data="stats")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ]
    await query.edit_message_text(stats_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def back_to_main(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    await start(query.message, context)

async def generate_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    chat_id = str(query.message.chat_id)

    if chat_id not in keys_data["user_keys"]:
        keyboard = [[InlineKeyboardButton("🔑 Get Premium Key", callback_data="get_key")]]
        return await query.edit_message_text(
            "🔒 *Premium Feature Locked* 🔒\n\nYou need a valid key to access the generator!",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    buttons = []
    for i in range(0, len(DOMAINS), 2):
        row = []
        if i < len(DOMAINS):
            row.append(InlineKeyboardButton(DOMAINS[i], callback_data=f"generate_{DOMAINS[i]}"))
        if i+1 < len(DOMAINS):
            row.append(InlineKeyboardButton(DOMAINS[i+1], callback_data=f"generate_{DOMAINS[i+1]}"))
        buttons.append(row)

    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main")])
    await query.edit_message_text("🛠 *Select a domain to generate:*", reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

async def generate_filtered_accounts(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    chat_id, selected_domain = str(query.message.chat_id), query.data.replace("generate_", "")
    if chat_id not in keys_data["user_keys"]:
        return await query.message.reply_text("🚨 You need a valid key to use this feature!")

    processing_msg = await query.message.reply_text("""
⚡ *Processing Your Request...*

🔍 Searching database...
🔄 Filtering accounts...
📦 Preparing download...
    
⌛ Estimated time: 2 seconds
""", parse_mode="Markdown")

    try:
        with open(USED_ACCOUNTS_FILE, "r", encoding="utf-8", errors="ignore") as f:
            used_accounts = set(f.read().splitlines())
    except:
        used_accounts = set()

    matched_lines = []
    for db_file in DATABASE_FILES:
        if len(matched_lines) >= LINES_TO_SEND:
            break
        try:
            with open(db_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    stripped = line.strip()
                    if selected_domain in stripped and stripped not in used_accounts:
                        matched_lines.append(stripped)
                        if len(matched_lines) >= LINES_TO_SEND:
                            break
        except:
            continue

    if not matched_lines:
        return await processing_msg.edit_text("❌ *No accounts available right now. Please try again later.*", parse_mode="Markdown")

    with open(USED_ACCOUNTS_FILE, "a", encoding="utf-8") as f:
        f.writelines("\n".join(matched_lines) + "\n")

    filename = f"{selected_domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(matched_lines))

    await asyncio.sleep(2)
    await processing_msg.delete()
    with open(filename, "rb") as f:
        await query.message.reply_document(InputFile(f, filename), caption=f"✅ *{len(matched_lines)} accounts generated!*", parse_mode="Markdown")
    os.remove(filename)

async def generate_key(update: Update, context: CallbackContext):
    if update.message.chat_id != ADMIN_ID:
        return await update.message.reply_text("🔒 *Admin only*", parse_mode="Markdown")

    if len(context.args) != 1:
        return await update.message.reply_text("⚠ Usage: /genkey <1h|1d|7d|lifetime>", parse_mode="Markdown")

    duration = context.args[0]
    new_key = generate_random_key()
    expiry = get_expiry_time(duration)
    keys_data["keys"][new_key] = expiry
    save_keys(keys_data)

    await update.message.reply_text(f"✅ *Key:* `{new_key}`\n⏳ *Expires:* `{duration}`", parse_mode="Markdown")

async def redeem_key_callback(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("🔑 Send your key with `/key YOUR_KEY`", parse_mode="Markdown")

async def redeem_key(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat_id)
    if len(context.args) != 1:
        return await update.message.reply_text("❗ Usage: `/key <YOUR_KEY>`", parse_mode="Markdown")

    entered_key = context.args[0]
    if entered_key not in keys_data["keys"]:
        return await update.message.reply_text("❌ *Invalid key.*", parse_mode="Markdown")

    expiry = keys_data["keys"][entered_key]
    if expiry and datetime.now().timestamp() > expiry:
        del keys_data["keys"][entered_key]
        save_keys(keys_data)
        return await update.message.reply_text("⌛ *Key expired.*", parse_mode="Markdown")

    keys_data["user_keys"][chat_id] = expiry
    del keys_data["keys"][entered_key]
    save_keys(keys_data)
    await update.message.reply_text("✅ *Key redeemed! You now have access.*", parse_mode="Markdown")

async def view_logs(update: Update, context: CallbackContext):
    if update.message.chat_id != ADMIN_ID:
        return await update.message.reply_text("❌ Admin only", parse_mode="Markdown")

    active = 0
    expired = 0
    text = "📋 *User Logs:*\n\n"
    for uid, expiry in keys_data["user_keys"].items():
        if expiry is None:
            status = "Lifetime"
            active += 1
        elif datetime.now().timestamp() > expiry:
            status = "Expired"
            expired += 1
        else:
            status = datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S')
            active += 1
        text += f"👤 `{uid}` - {status}\n"

    text += f"\n✅ Active: {active}\n❌ Expired: {expired}"
    await update.message.reply_text(text, parse_mode="Markdown")

# === RUN ===
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("genkey", generate_key))
    app.add_handler(CommandHandler("key", redeem_key))
    app.add_handler(CommandHandler("logs", view_logs))
    app.add_handler(CallbackQueryHandler(generate_menu, pattern="^generate_menu$"))
    app.add_handler(CallbackQueryHandler(generate_filtered_accounts, pattern="^generate_"))
    app.add_handler(CallbackQueryHandler(bot_info, pattern="^info$"))
    app.add_handler(CallbackQueryHandler(account_stats, pattern="^stats$"))
    app.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"))
    app.add_handler(CallbackQueryHandler(redeem_key_callback, pattern="^get_key$"))

    print("🤖 Bot is running on Railway!")
    app.run_polling()

if __name__ == "__main__":
    for f in DATABASE_FILES:
        if not os.path.exists(f):
            open(f, "w").close()
    if not os.path.exists(USED_ACCOUNTS_FILE):
        open(USED_ACCOUNTS_FILE, "w").close()
    main()
