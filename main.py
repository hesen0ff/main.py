ADMIN_ID = 6185398910
import os
from telegram import Update, ChatMember
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ChatMemberHandler
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type == "private":
        await update.message.reply_text(
            "🛡 SECURITY BOT AKTİVDİR\n\n"
            "Bu bot Telegram qruplarını qorumaq üçün hazırlanıb.\n\n"
            "➕ Qrupa əlavə et\n"
            "🔑 Admin et\n"
            "🔒 Qoruma avtomatik aktivləşəcək"
        )
    else:
        member = await context.bot.get_chat_member(chat.id, context.bot.id)
        if member.status not in ["administrator", "creator"]:
            await update.message.reply_text(
                "⚠️ Bot admin deyil.\nQoruma aktiv deyil."
            )
        else:
            await update.message.reply_text(
                "🛡 Security aktivdir.\nQrup nəzarət altındadır."
            )

async def bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_status = update.chat_member.new_chat_member.status
    if new_status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
        await context.bot.send_message(
            chat_id=update.chat_member.chat.id,
            text="✅ Təhlükəsizlik sistemi aktivləşdirildi."
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatMemberHandler(bot_added, ChatMemberHandler.MY_CHAT_MEMBER))
    app.run_polling()

if __name__ == "__main__":
    main()
