import os
import re
import time
import subprocess
import platform

if platform.system == 'Windows':
    # only exists and is only needed on windows
    import win32gui

from abc import ABC, abstractmethod
from queue import Queue
from threading import Thread

from pynput.keyboard import Key
from dataclasses import dataclass
from game.entities.player import CurrentPlayer

from game.logging.log_reader import EverQuestLogReader
from game.logging.entities.log_message import LogMessageType

from utils.output import send_text, send_multiple_keys, send_key
from utils.config import get_config
from utils.file import get_latest_modified_file


EVERQUEST_ROOT_FOLDER = get_config('game.root_folder')
EVERQUEST_LOG_FOLDER = os.path.join(EVERQUEST_ROOT_FOLDER, 'Logs')


class EverQuestWindow(ABC):

    def __init__(self, daemon: bool = True):
        self._queue = Queue()

        self.player = CurrentPlayer(
            name=get_config('player.name'),
            server=get_config('player.server'),
            guild=get_config('player.guild'))

        if get_config('player.autodetect'):
            if not self.player.name or not self.player.server:
                self._lookup_current_player()
            if not self.player.guild:
                self._lookup_current_guild()

        # Making the creation of the thread be the last thing that happens
        # so that the rest of initialization is done before it starts
        self._thread = Thread(target=self.run, daemon=daemon).start()

    @staticmethod
    def get_window(*args, **kwargs):
        ''' Returns an appropriate instantiated Window
            based on the platform being run (Windows, Mac, or Linux)
        '''
        window_class = {
            'Darwin': EverQuestWindow,
            'Linux': LinuxEverQuestWindow,
            'Windows': WindowsEverQuestWindow,
        }.get(platform.system(), EverQuestWindow)
        return window_class(*args, **kwargs)

    # Run this as a daemon so the thread will be cleaned up if the process is destroyed
    def run(self) -> None:
        while True:
            handler = self._queue.get(block=True)
            if not callable(handler):
                print(
                    f'Received an action of type {type(handler)}, rather than a function. The action will be ignored.',
                    flush=True)
                continue
            handler()

    def handle_window_action(self, action):
        self._queue.put(action)

    @abstractmethod
    def activate(self):
        pass

    def clear_chat(self):
        send_multiple_keys([Key.shift, Key.delete])
        send_key(Key.enter)

    def send_chat_message(self, message):
        self.clear_chat()
        send_text(message)
        send_key(Key.enter)

    def guild_dump(self, outputfile):
        self.activate()
        return self.send_chat_message(f"/outputfile guild {outputfile}")

    def get_player_log_reader(self):
        return EverQuestLogReader(EVERQUEST_LOG_FOLDER, self.player)

    def target(self, target):
        self.send_chat_message(f"/target {target}")

    def cast_spell(self, target, spell_name, spell_slot):
        self.send_chat_message(f"/cast {spell_slot}")

    def sit(self):
        self.send_chat_message("/sit")

    def _lookup_current_player(self):
        self.activate()
        self.send_chat_message("/log on")
        print('Looking up recently modified log file.')

        latest_file = get_latest_modified_file(f"{EVERQUEST_LOG_FOLDER}{os.path.sep}eqlog_*")
        if not latest_file:
            raise ValueError('Failed to find any log files. Is EverQuest running?')

        search_result = re.search(r"eqlog_(.*)_(.*).txt", os.path.split(latest_file)[-1])
        if not search_result or len(search_result.groups()) < 2:
            raise ValueError('Failed to parse player name and/or server from log file.')

        if not self.player.name:
            self.player.name = search_result.group(1)
        if not self.player.server:
            self.player.server = search_result.group(2).capitalize()

    def _update_current_guild(self, message):
        # TODO: Handle during parsing with concrete message classes
        search_result = re.search(r"is the rank of .* in (.*).$", message.full_message)
        self.player.guild = search_result.group(1)

    def _lookup_current_guild(self):
        log_reader = self.get_player_log_reader()
        log_reader.observe_messages(
            LogMessageType.GUILD_STAT,
            self._update_current_guild)

        self.activate()
        self.send_chat_message(f"/target {self.player.name}")
        self.send_chat_message(f"/guildstat")
        log_reader.process_new_messages()

        while not self.player.guild:
            log_reader.process_new_messages()
            print('Guild name has not been found. Waiting...')
            time.sleep(1)

        log_reader.remove_observation(
            LogMessageType.GUILD_STAT,
            self._update_current_guild)


class WindowsEverQuestWindow(EverQuestWindow):

    def _lookup(self):
        return win32gui.FindWindow(None, "EverQuest")

    def activate(self):
        win32gui.SetForegroundWindow(self._lookup())
        time.sleep(.5)


class LinuxEverQuestWindow(EverQuestWindow):

    def activate(self):
        # Find the EverQuest window. If more than one exists,
        # it'll be the first one returned by xdotool
        p = subprocess.run([
            "xdotool", "search",
            "--limit", "1",
            "--name", "^EverQuest$",
        ], capture_output=True)
        window_id = p.stdout.decode('utf-8').strip()

        # If the window is on another desktop, we need to
        # find which desktop, then focus it
        p = subprocess.run([
            "xdotool", "get_desktop_for_window",
            window_id,
        ], capture_output=True)
        desktop_id = p.stdout.decode('utf-8').strip()
        subprocess.run(["xdotool", "set_desktop", desktop_id])
        # Focus the window and wait until it has focus via --sync
        subprocess.run(["xdotool", "windowfocus", "--sync", window_id])

class MacEverQuestWindow(EverQuestWindow):

    def activate(self):
        # TODO: Is there a way to bring a window to foreground by name on Mac?
        # for now, just skipping activation.  The bot will work as long as
        # the EQ window remains in the foreground and focused
        pass

