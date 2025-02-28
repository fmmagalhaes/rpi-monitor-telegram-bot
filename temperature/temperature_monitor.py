import time
from helpers.logger_config import get_logger
from helpers.system_commands import get_cpu_temperature
from typing import Dict

logger = get_logger()


class TemperatureMonitor:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.current_threshold = None
        self.last_alerts: Dict[int, float] = {}

    def check_threshold_exceeded(self, current_temp, thresholds):
        """Check if any threshold is exceeded and return the highest one"""
        for threshold in thresholds:
            if current_temp >= threshold['value']:
                return threshold
        return None

    def get_severity_indicator(self, context, threshold_value):
        """Return severity indicator based on threshold"""
        config = context.application.bot_data['config']
        if threshold_value >= config['severity_levels']['high']:
            return "🔴"
        elif threshold_value >= config['severity_levels']['medium']:
            return "🟠"
        elif threshold_value >= config['severity_levels']['low']:
            return "🟡"
        else:
            return "⚪"

    async def handle_temperature_change(self, context, current_temp, exceeded_threshold):
        """Handle temperature changes and send appropriate messages"""
        # Case 1: Jumped between thresholds or interval elapsed
        if exceeded_threshold and (exceeded_threshold['value'] != self.current_threshold or time.time() - self.last_alerts.get(exceeded_threshold['value'], 0) > exceeded_threshold['interval']):
            self.last_alerts[exceeded_threshold['value']] = time.time()
            self.current_threshold = exceeded_threshold['value']

            severity = self.get_severity_indicator(context, exceeded_threshold['value'])

            message = f"{severity} Temperature is {current_temp}°C"
            logger.warning(message)
            await context.bot.send_message(chat_id=self.chat_id, text=message)

        # Case 2: Temperature has fallen below all thresholds
        elif not exceeded_threshold and self.current_threshold is not None:
            self.current_threshold = None

            message = f"✅ Temperature back to normal: {current_temp}°C"
            logger.info(message)

            await context.bot.send_message(chat_id=self.chat_id, text=message)

    async def check_temperature(self, context):
        """Check temperature and handle alerts"""
        try:
            current_temp = float(get_cpu_temperature().replace('°C', ''))

            thresholds = sorted(
                context.application.bot_data['config']['thresholds'],
                key=lambda x: x['value'],
                reverse=True
            )

            exceeded_threshold = self.check_threshold_exceeded(current_temp, thresholds)
            await self.handle_temperature_change(context, current_temp, exceeded_threshold)
        except Exception as e:
            logger.error(f"An error occurred while evaluating the temperature: {str(e)}")
            return
