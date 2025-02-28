from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext
from helpers.logger_config import get_logger

logger = get_logger()


def execute_with_authentication(func):
    @wraps(func)
    async def wrapper(update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        chat_id = context.application.bot_data['config']['telegram']['chat_id']

        if user_id != chat_id:
            logger.warning(f"Unauthorized access attempt by user_id: {user_id}")
            return

        return await func(update, context)

    return wrapper
