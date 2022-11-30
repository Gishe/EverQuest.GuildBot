import time
import action_queue

from datetime import timedelta
from game.window import EverQuestWindow
from game.guild.guild_tracker import GuildTracker
from utils.input import has_recent_input, get_timedelta_since_input
from game.logging.entities.log_message import LogMessageType
from game.buff.buff_manager import BuffManager
from game.dkp.bidding_manager import BiddingManager
from integrations.opendkp.opendkp import OpenDkp
from utils.config import get_config
import logging

TICK_INTERVAL = 1

class Bot:
    def __init__(self):
        self._window = EverQuestWindow.get_window()
        self._player_log_reader = self._window.get_player_log_reader()
        self._opendkp = OpenDkp()
        self._guild_tracker = GuildTracker(
            self._window,
            self._opendkp)
        log_level = get_config('logging.level', 'DEBUG')
        numeric_level = getattr(logging, log_level, None)
        if not isinstance(numeric_level, int):
            logging.basicConfig(filename=get_config('logging.file_name', "eq_bot.log"), level=numeric_level)
        else:
            raise ValueError('Invalid log level: %s' % log_level)

    def run(self):
        # Configure DKP Bidding Manager
        if get_config('dkp.bidding.enabled'):
            bidding_manager = BiddingManager(
                self._window,
                self._guild_tracker,
                self._opendkp)

            self._player_log_reader.observe_messages(
                LogMessageType.TELL_RECEIVE,
                bidding_manager.handle_tell_message)

        # Configure Buffing Manager
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

        # Start a thread to continuously track guild members
        if get_config('guild_tracking.enabled'):
            self._guild_tracker.start()
        
        # Start the action queue, which will begin processing commands to the window/other services synchronously
        action_queue.start()

        # This thread is probably processing the signal handlers, so we need to let it run every so often
        while True:
            time.sleep(TICK_INTERVAL)
