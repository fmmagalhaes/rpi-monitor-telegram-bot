from helpers.system_commands import system_uptime
from helpers.logger_config import get_logger
from helpers.auth_wrapper import execute_with_authentication

logger = get_logger()


@execute_with_authentication
async def uptime_handler(update, context):
    logger.info(f"Uptime check requested by user {update.effective_user.id}")

    success, message = system_uptime()
    if success:
        await update.message.reply_text(message.replace("up", "System has been up for"))
    else:
        await update.message.reply_text(f'❌ Error: {message}')
