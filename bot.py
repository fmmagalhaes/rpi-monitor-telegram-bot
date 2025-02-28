import asyncio
import os
import yaml
from handlers.start_handler import start_handler
from handlers.status_handler import status_handler
from handlers.uptime_handler import uptime_handler
from handlers.reboot_handler import reboot_handler
from handlers.shutdown_handler import shutdown_handler
from handlers.error_handler import error_handler
from helpers.auth_wrapper import execute_with_authentication
from helpers.logger_config import setup_logger
from telegram.ext import ApplicationBuilder, CommandHandler
from temperature.temperature_monitor import TemperatureMonitor

CURRENT_DIR = os.path.dirname(__file__)
logger = setup_logger(CURRENT_DIR)


def load_config():
    config_path = os.path.join(CURRENT_DIR, 'config.yml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


async def send_startup_message(context):
    try:
        await context.bot.send_message(
            chat_id=context.application.bot_data['config']['telegram']['chat_id'],
            text="🤖 Raspberry Pi Bot is now online!\n\nSystem monitoring services are active."
        )
        context.job.schedule_removal()
    except Exception as e:
        logger.warning(f"Failed to send startup message: {e}. Retrying later...")


def main():
    try:
        config = load_config()
        telegram_config = config['telegram']

        application = ApplicationBuilder().token(telegram_config['token']).build()
        application.bot_data['config'] = config

        application.add_handler(CommandHandler("start", execute_with_authentication(start_handler)))
        application.add_handler(CommandHandler("help", execute_with_authentication(start_handler)))
        application.add_handler(CommandHandler("status", execute_with_authentication(status_handler)))
        application.add_handler(CommandHandler("uptime", execute_with_authentication(uptime_handler)))
        application.add_handler(CommandHandler("shutdown", execute_with_authentication(shutdown_handler)))
        application.add_handler(CommandHandler("reboot", execute_with_authentication(reboot_handler)))
        application.add_error_handler(error_handler)

        monitor = TemperatureMonitor(telegram_config['chat_id'])

        application.job_queue.run_repeating(
            send_startup_message,
            interval=30,
            first=5,
        )
        application.job_queue.run_repeating(
            monitor.check_temperature,
            interval=60,
            first=30
        )

        logger.info("Starting bot...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise


if __name__ == '__main__':
    asyncio.run(main())
