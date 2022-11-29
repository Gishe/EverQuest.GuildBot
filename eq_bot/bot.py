import time
from datetime import timedelta
from game.window import EverQuestWindow
from game.guild.guild_tracker import GuildTracker
from utils.input import has_recent_input, get_timedelta_since_input
from game.logging.entities.log_message import LogMessageType
from game.buff.buff_manager import BuffManager
from utils.config import get_config

TICK_INTERVAL = 1

class Bot:
    def __init__(self):
        self._window = EverQuestWindow()
        self._player_log_reader = self._window.get_player_log_reader()
        self._guild_tracker = GuildTracker(self._window)

    def run(self):
        # Starts a thread which manages a queue of actions to be performed by the window
        self._window.start()
            
        # Configure log message subscriptions
        if get_config('buffing.enabled'):
            buff_manager = BuffManager(
                self._window,
                self._guild_tracker)

            self._player_log_reader.observe_messages(
                LogMessageType.TELL_RECEIVE,
                buff_manager.handle_tell_message)

        # Starts a thread that continuously monitors the log
        if get_config('log_parsing.enabled', True):
            self._player_log_reader.start()

        if get_config('guild_tracking.enabled'):
            self._guild_tracker.start()

        # This thread is probably processing the signal handlers, so we need to let it run every so often
        while True:
            time.sleep(TICK_INTERVAL)
