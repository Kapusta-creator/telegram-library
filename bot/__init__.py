from telegram import *
from app import *
import threading


class FlaskThread(threading.Thread):
    def run(self) -> None:
        app.run(host = "0.0.0.0", port=8080)


class TelegramThread(threading.Thread):
    def run(self) -> None:
        bot.run()


if __name__ == '__main__':
    flask_thread = FlaskThread()
    bot_thread = TelegramThread()
    flask_thread.start()
    bot_thread.start()

