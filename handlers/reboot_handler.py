from helpers.system_commands import system_reboot
from helpers.logger_config import get_logger

logger = get_logger()


async def reboot_handler(update, context):
    logger.info(f"Reboot requested by user {update.effective_user.id}")

    await update.message.reply_text('🔄 Rebooting the system... This can take up to 3 minutes')

    success, message = system_reboot()
    if not success:
        await update.message.reply_text(f'❌ Error: {message}')
