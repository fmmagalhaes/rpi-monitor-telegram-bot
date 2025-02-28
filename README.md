# Raspberry Pi Telegram Bot

A Telegram bot designed to monitor the temperature of a Raspberry Pi and perform basic system commands.

## Features

- **Temperature Monitoring**: Continuously monitors the temperature of your Raspberry Pi and provides alerts when thresholds are exceeded.
- **System Commands**: Allows you to perform basic system commands such as reboot, shutdown, or get system information.

## Creating a Telegram Bot

Start a chat with [@BotFather](https://telegram.me/BotFather) and use the `/newbot` command to create your bot.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/fmmagalhaes/rpi-monitor-telegram-bot.git
    cd rpi-monitor-telegram-bot
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Copy the example configuration file and edit it with your details:
    ```sh
    cp config.example.yml config.yml
    ```

4. Run the bot:
    ```sh
    python bot.py
    ```

## Usage

- **/start**: List all available commands
- **/status**: Check system metrics
- **/uptime**: Check system uptime
- **/reboot**: Reboot the system
- **/shutdown**: Shutdown the system
