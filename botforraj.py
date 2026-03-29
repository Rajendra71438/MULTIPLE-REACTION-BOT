import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN = os.getenv("ADMIN_USERNAME")
CHANNEL = os.getenv("CHANNEL_LINK")
IMAGE = os.getenv("WELCOME_IMAGE")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

users = set()
leads = {}

# 🔥 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users.add(user.id)

    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    await asyncio.sleep(1)

    text = "👋 Welcome back!" if user.id in leads else "👋 Welcome!"

    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL)],
        [InlineKeyboardButton("📢 Meta Ads", callback_data="meta")],
        [InlineKeyboardButton("🌐 Landing Pages", callback_data="landing")],
        [InlineKeyboardButton("📱 Hack APK", callback_data="apk")],
        [InlineKeyboardButton("🤖 Bots", callback_data="bots")],
        [InlineKeyboardButton("📩 Contact", url=f"https://t.me/{ADMIN.replace('@','')}")]
    ]

    caption = f"""
{text}

🚀 Grow with our services:

📢 Meta Ads  
🌐 Landing Pages  
📱 Hack APK  
🎬 Ads Videos  
🤖 Telegram Bots  

👇 Choose below
"""

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=IMAGE,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🔁 MENU BACK
def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="start")]
    ])

# 📢 META ADS
async def meta(update, context):
    keyboard = [
        [InlineKeyboardButton("📅 Weekly ₹2500", callback_data="lead_meta_week")],
        [InlineKeyboardButton("📆 Monthly ₹10000", callback_data="lead_meta_month")],
        [InlineKeyboardButton("🔙 Back", callback_data="start")]
    ]
    await update.callback_query.edit_message_text("📢 Meta Ads Plans:", reply_markup=InlineKeyboardMarkup(keyboard))

# 🌐 LANDING
async def landing(update, context):
    text = """🌐 Landing Pages

💰 Basic: ₹500–₹800  
💎 Premium: ₹1000–₹1500  

🔥 High conversion pages"""
    await update.callback_query.edit_message_text(text, reply_markup=back_button())

# 📱 APK
async def apk(update, context):
    text = """📱 Hack APK

💰 Price depends on features

📩 Contact for details"""
    await update.callback_query.edit_message_text(text, reply_markup=back_button())

# 🤖 BOTS
async def bots(update, context):
    text = """🤖 Telegram Bots

💰 ₹500/month basic  
⚡ Advanced custom pricing"""
    await update.callback_query.edit_message_text(text, reply_markup=back_button())

# 🧠 LEAD CAPTURE
async def lead_start(update, context):
    query = update.callback_query
    user = query.from_user

    leads[user.id] = {"service": query.data}
    await query.message.reply_text("📝 Enter your name:")
    context.user_data["step"] = "name"

# 📩 HANDLE TEXT (AUTO REPLY + LEAD)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user = update.effective_user

    # 🔥 Keyword replies
    if "price" in text:
        await update.message.reply_text("💰 Pricing depends on service. Basic starts ₹500.")
        return
    elif "bot" in text:
        await update.message.reply_text("🤖 We create automation bots for your business.")
        return
    elif "ads" in text:
        await update.message.reply_text("📢 We run high ROI Meta ads.")
        return

    # 🔥 Lead capture flow
    if context.user_data.get("step") == "name":
        leads[user.id]["name"] = text
        await update.message.reply_text("💰 Enter your budget:")
        context.user_data["step"] = "budget"

    elif context.user_data.get("step") == "budget":
        leads[user.id]["budget"] = text
        await update.message.reply_text("📌 What service do you need?")
        context.user_data["step"] = "done"

        # send to admin
        data = leads[user.id]
        await context.bot.send_message(
            ADMIN_ID,
            f"🔥 New Lead\nName: {data['name']}\nBudget: {data['budget']}\nService: {data['service']}"
        )

# 📢 BROADCAST
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    msg = " ".join(context.args)
    for user in users:
        try:
            await context.bot.send_message(user, msg)
        except:
            pass

    await update.message.reply_text("✅ Broadcast sent")

# 🔁 CALLBACK ROUTER
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data

    if data == "start":
        await start(update, context)
    elif data == "meta":
        await meta(update, context)
    elif data == "landing":
        await landing(update, context)
    elif data == "apk":
        await apk(update, context)
    elif data == "bots":
        await bots(update, context)
    elif data.startswith("lead_"):
        await lead_start(update, context)

# 🚀 MAIN
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🔥 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()