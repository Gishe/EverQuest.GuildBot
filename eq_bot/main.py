import signal
import sys

from utils.config import get_config

from integrations.discord import send_bot_started_message, send_bot_stopped_message, send_bot_crashed_message

from bot import Bot

_crash_notification_sent = False


def on_start():
    print('Bot has been started.')
    if get_config('monitoring.notifications.notify_on_start'):
        send_bot_started_message()


def on_stop():
    print('Bot has been stopped.')
    if get_config('monitoring.notifications.notify_on_stop') and not _crash_notification_sent:
        send_bot_stopped_message()


def on_crash(e: Exception):
    print(f'Bot has crashed: {e}')

    if get_config('monitoring.notifications.notify_on_crash'):
        send_bot_crashed_message()
        global _crash_notification_sent
        _crash_notification_sent = True

    # Reraise so that the stack trace is printed
    raise e


def main():
    try:
        on_start()
        Bot().run()
    except Exception as e:
        on_crash(e)
    finally:
        on_stop()


if __name__=='__main__':
    main()


def sig_handler(_signo, _stack_frame):
    on_stop()
    sys.exit(0)


signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGINT, sig_handler)
