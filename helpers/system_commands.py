import subprocess
import psutil
from helpers.logger_config import get_logger

logger = get_logger()


def get_cpu_temperature():
    temp = subprocess.check_output(['vcgencmd', 'measure_temp']).decode()
    return temp.replace('temp=', '').replace('\'C', '°C')


def get_system_status():
    try:
        cpu_usage = psutil.cpu_percent()

        ram = psutil.virtual_memory()
        ram_total = convert_to_gb(ram.total)
        ram_used = convert_to_gb(ram.used)

        disk = psutil.disk_usage('/')
        disk_total = convert_to_gb(disk.total)
        disk_used = convert_to_gb(disk.used)

        temperature = get_cpu_temperature()

        logger.info("System status collected")

        return {
            'cpu_usage': cpu_usage,
            'ram_used': ram_used,
            'ram_total': ram_total,
            'disk_used': disk_used,
            'disk_total': disk_total,
            'temperature': temperature,
            'success': True
        }
    except Exception as e:
        error_msg = f"Failed to collect system status: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg
        }


def system_uptime():
    return execute_system_command(['uptime', '-p'], "Uptime")


def system_reboot():
    return execute_system_command(['sudo', 'reboot'], "Reboot")


def system_shutdown():
    return execute_system_command(['sudo', 'shutdown', '-h', 'now'], "Shutdown")


def convert_to_gb(bytes_value):
    return round(bytes_value / (1024.0 ** 3), 1)


def execute_system_command(command: list, action: str):
    try:
        logger.info(f"Initiating system {action}...")
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"{action} initiated successfully: {result.stdout}")
            return True, result.stdout
        else:
            error_msg = f"{action} failed: {result.stderr}"
            logger.error(error_msg)
            return False, error_msg
    except Exception as e:
        error_msg = f"Failed to execute {action}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
