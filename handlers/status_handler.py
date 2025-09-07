from helpers.logger_config import get_logger
from helpers.system_commands import get_system_status
from helpers.auth_wrapper import execute_with_authentication

logger = get_logger()


@execute_with_authentication
async def status_handler(update, context):
    logger.info(f"status requested by user {update.effective_user.id}")

    status_data = get_system_status()
    if status_data['success']:
        message = (f"📊 System Status\n\n"
                   f"⚙️ CPU Usage: {status_data['cpu_usage']}%\n"
                   f"💾 RAM: {status_data['ram_used']}GB of {status_data['ram_total']}GB\n"
                   f"📂 Disk: {status_data['disk_used']}GB of {status_data['disk_total']}GB\n"
                   f"🌡️ Temperature: {status_data['temperature']}")
    else:
        message = f"❌ Error collecting system metrics: {status_data['error']}"

    await update.message.reply_text(message)
    logger.info(f"status response sent to user {update.effective_user.id}")
