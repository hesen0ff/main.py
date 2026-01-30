import os
import time
from collections import defaultdict
from telegram import Update, ChatMember
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ChatMemberHandler,
    MessageHandler, 
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6185398910

# Flood üçün yaddaş
user_messages = defaultdict(list)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    # adminə bildiriş
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 /start\n👤 {user.first_name}\n🆔 {user.id}\n@{user.username}"
    )

    if chat.type == "private":
        await update.message.reply_text(
            "🛡 SECURITY BOT AKTİVDİR\n\n"
            "Admin olduğum qrupları avtomatik qoruyuram.\n\n"
            "🔐 Anti-link\n"
            "🤖 Anti-bot\n"
            "⛔ Anti-flood"
        )

# Link qoruması
async def anti_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat = update.effective_chat

    member = await context.bot.get_chat_member(chat.id, context.bot.id)
    if member.status not in ["administrator", "creator"]:
        return

    if message.entities:
        for e in message.entities:
            if e.type in ["url", "text_link"]:
                await message.delete()
                await message.reply_text("🚫 Link qadağandır.")
                await context.bot.send_message(
                    ADMIN_ID,
                    f"🚫 Link silindi\n👤 {message.from_user.first_name}\n🆔 {message.from_user.id}"
                )
                break

# Flood qoruması
async def anti_flood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    now = time.time()
    user_messages[user.id].append(now)
    user_messages[user.id] = [t for t in user_messages[user.id] if now - t < 5]

    if len(user_messages[user.id]) >= 6:
        await context.bot.restrict_chat_member(
            chat.id,
            user.id,
            permissions=None,
            until_date=int(now + 60)
        )
        await update.message.reply_text("⛔ Flood! 1 dəqiqə mute.")
        await context.bot.send_message(
            ADMIN_ID,
            f"⛔ Flood mute\n👤 {user.first_name}\n🆔 {user.id}"
        )

# Bot əlavə ediləndə kick
async def anti_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.chat_member.chat
    new = update.chat_member.new_chat_member

    if new.user.is_bot and new.user.id != context.bot.id:
        await context.bot.ban_chat_member(chat.id, new.user.id)
        await context.bot.send_message(
            ADMIN_ID,
            f"🤖 Bot kick edildi\n🤖 {new.user.username}"
        )

# Bot admin ediləndə xəbər
async def bot_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_status = update.chat_member.new_chat_member.status
    if new_status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
        await context.bot.send_message(
            update.chat_member.chat.id,
            "✅ Security aktivdir. Qrup nəzarət altındadır."
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_link))
    app.add_handler(MessageHandler(filters.ALL, anti_flood))
    app.add_handler(ChatMemberHandler(anti_bot, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(ChatMemberHandler(bot_admin, ChatMemberHandler.MY_CHAT_MEMBER))

    app.run_polling()

if __name__ == "__main__":
    main()
