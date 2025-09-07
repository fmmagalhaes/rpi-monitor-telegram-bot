from helpers.logger_config import get_logger
from helpers.auth_wrapper import execute_with_authentication

logger = get_logger()


@execute_with_authentication
async def start_handler(update, context):
    """Send a message when the command /start is issued."""
    try:
        await update.message.reply_text('Available commands:\n'
                                        '/status - Check system metrics\n'
                                        '/uptime - Check system uptime\n'
                                        '/reboot - Restart the system\n'
                                        '/shutdown - Shutdown the system')
        logger.info("Start command executed successfully")
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        try:
            await update.message.reply_text('Error starting bot')
        except:
            logger.error("Could not send error message to user")
