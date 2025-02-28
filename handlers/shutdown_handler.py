from helpers.system_commands import system_shutdown
from helpers.logger_config import get_logger

logger = get_logger()


async def shutdown_handler(update, context):
    logger.info(f"Shutdown requested by user {update.effective_user.id}")

    await update.message.reply_text('🔄 Shutting down the system...')

    success, message = system_shutdown()
    if not success:
        await update.message.reply_text(f'❌ Error: {message}')
