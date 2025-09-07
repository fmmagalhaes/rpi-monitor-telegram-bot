import math
import time
from helpers.logger_config import get_logger
from helpers.system_commands import get_cpu_temperature
from typing import Dict

HIGH = "🔴"
MEDIUM = "🟠"
LOW = "🟡"

logger = get_logger()


class TemperatureMonitor:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.current_threshold = None
        # Timestamp when temp first exceeded threshold
        self.exceeded_since: Dict[int, float] = {}
        self.recovered_since: Dict[int, float] = {}  # Track recovery durations
        self.alerted_thresholds: Dict[int, bool] = {}  # Track if alert was sent for a threshold

    def get_severity_indicator(self, context, threshold_value):
        """Dynamically determine severity based on threshold values"""
        thresholds = context.application.bot_data['config']['thresholds']
        thresholds = sorted(thresholds, key=lambda t: t['value'], reverse=True)

        middle_index = len(thresholds) // 2
        if threshold_value >= thresholds[0]['value']:
            return HIGH
        elif threshold_value >= thresholds[middle_index]['value']:
            return MEDIUM
        else:
            return LOW

    def check_exceeded_thresholds(self, current_temp, thresholds):
        """Return all exceeded thresholds."""
        return [t for t in thresholds if current_temp >= t['value']]

    async def handle_temperature_change(self, context, current_temp, sorted_exceeded_thresholds):
        """Handle temperature changes and send appropriate messages."""
        current_time = time.time()
        await self.handle_temperature_rise(context, current_time, current_temp, sorted_exceeded_thresholds)
        await self.handle_recovery(context, current_time, current_temp, sorted_exceeded_thresholds)

    async def handle_temperature_rise(self, context, current_time, current_temp, sorted_exceeded_thresholds):
        # Remove thresholds that are no longer exceeded
        for threshold_value in list(self.exceeded_since.keys()):
            if threshold_value not in [t['value'] for t in sorted_exceeded_thresholds]:
                self.recovered_since[threshold_value] = current_time  # Start tracking recovery time
                del self.exceeded_since[threshold_value]

        # Track when each threshold was first exceeded
        for threshold in sorted_exceeded_thresholds:
            if threshold['value'] not in self.exceeded_since:
                self.exceeded_since[threshold['value']] = current_time

        # Find the highest threshold that has met its duration requirement
        for threshold in sorted_exceeded_thresholds:
            threshold_value = threshold['value']
            duration_required = threshold.get('duration', 0)
            elapsed = math.ceil(current_time - self.exceeded_since[threshold_value])

            if elapsed >= duration_required:
                self.current_threshold = threshold_value
                self.exceeded_since[threshold_value] = current_time

                severity = self.get_severity_indicator(context, current_temp)

                message = f"{severity} Temperature is {current_temp}°C"
                logger.warning(f"{message} (exceeded {threshold_value}°C for more than {duration_required} seconds)")

                await context.bot.send_message(chat_id=self.chat_id, text=message)

                self.alerted_thresholds[threshold_value] = True

                # Reset timers for all thresholds
                # This avoids unnecessary sequential alerts
                self.exceeded_since.clear()
                self.recovered_since.clear()

                break
            else:
                logger.warning(f"Temperature is {current_temp}°C (exceeded {threshold_value}°C, but only for {round(elapsed)} seconds) - Will not send message")

    async def handle_recovery(self, context, current_time, current_temp, exceeded_thresholds):
        # Temperature has fallen below all thresholds
        if not exceeded_thresholds and self.current_threshold is not None:
            self.current_threshold = None
            message = f"✅ Temperature back to normal: {current_temp}°C"
            logger.info(message)
            await context.bot.send_message(chat_id=self.chat_id, text=message)

            self.exceeded_since.clear()
            self.recovered_since.clear()
            self.alerted_thresholds.clear()

        else:
            # Temperature has remained below the threshold (but still above another) for <duration> seconds.
            # The same <duration> configuration is used for recovery as for the exceedance.
            # This means that if we alert after exceeding 80 degrees for 5 minutes, we also alert if the temperature stays below 80 for 5 minutes.
            # This ensures we receive recovery feedback without having to wait too long.
            for threshold_value, start_time in list(self.recovered_since.items()):
                if current_temp >= threshold_value:
                    del self.recovered_since[threshold_value]
                else:
                    thresholds = context.application.bot_data['config']['thresholds']
                    matching_threshold = next((threshold for threshold in thresholds if threshold['value'] == threshold_value))
                    duration_required = matching_threshold.get('duration', 0)
                    recovery_elapsed = math.ceil(current_time - start_time)

                    if recovery_elapsed >= duration_required and self.alerted_thresholds.get(threshold_value, False):
                        severity = self.get_severity_indicator(context, current_temp)

                        message = f"{severity} Temperature is {current_temp}°C"
                        logger.warning(f"{message} (kept below {threshold_value}°C for more than {duration_required} seconds)")

                        await context.bot.send_message(chat_id=self.chat_id, text=message)

                        self.alerted_thresholds.clear()
                        self.exceeded_since.clear()
                        self.recovered_since.clear()
                        break

    async def check_temperature(self, context):
        """Check temperature and handle alerts."""
        try:
            current_temp = float(get_cpu_temperature().replace('°C', ''))

            thresholds = sorted(
                context.application.bot_data['config']['thresholds'],
                key=lambda x: x['value'],
                reverse=True
            )

            exceeded_thresholds = self.check_exceeded_thresholds(current_temp, thresholds)
            await self.handle_temperature_change(context, current_temp, exceeded_thresholds)
        except Exception as e:
            logger.error(f"An error occurred while evaluating the temperature: {str(e)}")
            return
