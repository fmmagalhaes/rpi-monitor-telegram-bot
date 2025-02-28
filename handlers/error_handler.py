from helpers.logger_config import get_logger

logger = get_logger()


async def error_handler(update, context):
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ An error occurred while processing your request.")
