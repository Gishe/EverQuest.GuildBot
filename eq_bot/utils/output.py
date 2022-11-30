import random
from tkinter import Tk
from time import sleep
from utils.config import get_config
from pynput.keyboard import Key, Controller

MIN_MESSAGE_DELAY = get_config('general.output.min_message_delay', .75)
MAX_MESSAGE_DELAY = get_config('general.output.max_message_delay', 1)
MIN_KEY_DELAY = get_config('general.output.min_key_delay', .1)
MAX_KEY_DELAY = get_config('general.output.max_key_delay', .225)

# TODO: Send commands to process in background rather than sending keypresses to current screen
_keyboard = Controller()

_input_observers = []

def _sleep_message():
    sleep(random.uniform(MIN_MESSAGE_DELAY, MAX_MESSAGE_DELAY))

def _sleep_keypress(modifier = 1.0):
    sleep(random.uniform(MIN_KEY_DELAY * modifier, MAX_KEY_DELAY * modifier))

def _copy_to_clipboard(text):
    # create gui window
    gui_window = Tk()
    gui_window.withdraw()
    gui_window.clipboard_clear()
    # copy to window's clipboard
    gui_window.clipboard_append(text)
    # persist beyond window
    gui_window.update()
    # close window
    gui_window.destroy()

def send_key(key):
    _keyboard.press(key)
    _keyboard.release(key)
    _sleep_keypress()

def send_text(text):
    _copy_to_clipboard(text)
    send_multiple_keys([Key.ctrl_l, 'v'])
    _sleep_message()

def send_multiple_keys(keys):
    for key in keys:
        _keyboard.press(key)
        _sleep_keypress(.33)

    for key in keys:
        _keyboard.release(key)
        _sleep_keypress(.33)
