import asyncio
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram import Update, ReactionTypeEmoji

load_dotenv()

BOT_TOKENS = [
    os.getenv("TOKEN_1"), os.getenv("TOKEN_2"), os.getenv("TOKEN_3"),
    os.getenv("TOKEN_4"), os.getenv("TOKEN_5"), os.getenv("TOKEN_6"),
    os.getenv("TOKEN_7"), os.getenv("TOKEN_8"), os.getenv("TOKEN_9"),
    os.getenv("TOKEN_10"), os.getenv("TOKEN_11"), os.getenv("TOKEN_12"),
    os.getenv("TOKEN_13"), os.getenv("TOKEN_14"), os.getenv("TOKEN_15"),
    os.getenv("TOKEN_16"), os.getenv("TOKEN_17"), os.getenv("TOKEN_18"),
    os.getenv("TOKEN_19"), os.getenv("TOKEN_20"),
]

# ✅ Only 5 reactions
REACTIONS = ["❤️", "🔥", "😍", "🤩", "💯"]

apps = []

# Assign 4 bots per emoji
def get_emoji(index):
    return REACTIONS[index // 4]  # 0-3 same, 4-7 same, etc.


async def make_reactor(emoji):
    async def react(update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.effective_message
        if not msg:
            return
        try:
            await context.bot.set_message_reaction(
                chat_id=msg.chat_id,
                message_id=msg.message_id,
                reaction=[ReactionTypeEmoji(emoji)],
                is_big=True
            )
        except:
            pass  # silent
    return react


async def main():
    for i, token in enumerate(BOT_TOKENS):
        if not token:
            continue

        emoji = get_emoji(i)

        app = ApplicationBuilder().token(token).build()
        handler = await make_reactor(emoji)

        app.add_handler(MessageHandler(
            filters.TEXT | filters.PHOTO | filters.VIDEO,
            handler
        ))

        apps.append(app)

    # Start bots
    await asyncio.gather(*(app.initialize() for app in apps))
    await asyncio.gather(*(app.start() for app in apps))
    await asyncio.gather(*(app.updater.start_polling() for app in apps))

    print(f"🚀 {len(apps)} bots running with 5 reaction types")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await asyncio.gather(*(app.updater.stop() for app in apps))
        await asyncio.gather(*(app.stop() for app in apps))
        await asyncio.gather(*(app.shutdown() for app in apps))


if __name__ == "__main__":
    asyncio.run(main())