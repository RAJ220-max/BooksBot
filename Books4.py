from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

ADMIN_CHAT_ID = 5919948113  # Replace with your Telegram ID

def save_user(user_id):
    with open("users.txt", "a") as f:
        f.write(str(user_id) + "\n")

def load_users():
    try:
        with open("users.txt", "r") as f:
            return set(map(int, f.readlines()))
    except FileNotFoundError:
        return set()

user_ids = load_users()
broadcast_mode = {}

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Bot Library", callback_data="library")],
        [InlineKeyboardButton("🇮🇳 Indian Books", callback_data="indian_books")],
        [InlineKeyboardButton("💎 Sponsored", callback_data="sponsored")],
        [InlineKeyboardButton("📖 Which Book Do You Want?", callback_data="book_request")]
    ])

def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_ids.add(chat_id)
    save_user(chat_id)

    await context.bot.send_message(chat_id=chat_id, text="""
📚 *Welcome to  "Books India Bot" *

We provide any book PDF in ₹19 only.

✅ Steps:
1️⃣ Send Book Name & Author
2️⃣ Pay ₹19 via QR
3️⃣ Get book within 24 hours
    """, parse_mode="Markdown")

    try:
        with open("/storage/emulated/0/Download/paytm_qr.jpg","rb") as qr:
            await context.bot.send_photo(chat_id=chat_id, photo=qr)
    except:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ QR image not found.")

    await context.bot.send_message(chat_id=chat_id, text="Choose an option 👇", reply_markup=main_menu())

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "library":
        await query.edit_message_text("📚 Categories:\n- Self-help\n- Motivation\n- Novels\n- UPSC\n- Science", reply_markup=back_button())
    elif query.data == "indian_books":
        await query.edit_message_text("🇮🇳 Indian Books:\n- Wings of Fire\n- India 2020\n- White Tiger", reply_markup=back_button())
    elif query.data == "sponsored":
        await query.edit_message_text("💎 Sponsored Section\nPromote your content here.\nContact Admin.", reply_markup=back_button())
    elif query.data == "book_request":
        await query.edit_message_text("📖 Please send the Book Name & Author.\nYou'll receive the book within 24h after payment.", reply_markup=back_button())
    elif query.data == "main_menu":
        await query.edit_message_text("Choose an option 👇", reply_markup=main_menu())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    msg = update.message.text

    if chat_id not in user_ids:
        user_ids.add(chat_id)
        save_user(chat_id)

    await update.message.reply_text(f"✅ Book request received:\n*{msg}*", parse_mode="Markdown")
    await update.message.reply_text("🕒 You'll get the book in 24 hours.\n💰 Pay ₹19 via QR below.", parse_mode="Markdown")

    try:
        with open("/storage/emulated/0/Download/paytm_qr.jpg", "rb") as qr:
            await context.bot.send_photo(chat_id=chat_id, photo=qr)
    except:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ QR image not found.")

    await update.message.reply_text("📸 After payment, send screenshot here.")

    admin_msg = f"""
📥 *New Request:*

👤 {user.first_name} @{user.username or 'N/A'}
🆔 {user.id}
📝 {msg}
    """
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg, parse_mode="Markdown")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    broadcast_mode["active"] = True
    await update.message.reply_text("📢 Send your message to broadcast.")

if __name__ == '__main__':
    app = ApplicationBuilder().token("7986527254:AAGvYR50Pdiin3d7ZA4bJogQ5BZgnMPYS5g").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ra7lab_mode", broadcast))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_message))

    print("✅ Bot is running...")
    app.run_polling()
