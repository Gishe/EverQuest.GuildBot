import time
from datetime import timedelta
from game.window import EverQuestWindow
from game.guild.guild_tracker import GuildTracker
from utils.input import has_recent_input, get_timedelta_since_input
from game.entities.player import CurrentPlayer
from game.logging.entities.log_message import LogMessageType
from game.buff.buff_manager import BuffManager
from utils.config import get_config

EQ_SERVER = get_config('server')
# TODO: Automatically lookup on initialization by checking output of /character command
EQ_PLAYER = get_config('player')
TICK_LENGTH = 1

current_player = CurrentPlayer(name=EQ_PLAYER, server=EQ_SERVER)

window = EverQuestWindow(current_player)
player_log_reader = window.get_player_log_reader()

guild_tracker = GuildTracker(window)

# Configure log message subscriptions
if get_config('buffing.enabled'):
    buff_manager = BuffManager(window, guild_tracker)
    player_log_reader.observe_messages(LogMessageType.TELL_RECEIVE, buff_manager.handle_tell_message)

# Example log reader subscription. This will print all tells which are received.
player_log_reader.observe_messages(LogMessageType.TELL_RECEIVE, lambda message: message.print())

# Configure services which need to be activated periodically
while(True):
    if not has_recent_input():
        if get_config('log_parsing.enabled', True):
            player_log_reader.process_new_messages()
        if get_config('guild_tracking.enabled'):
            guild_tracker.handle_tick()
    time.sleep(TICK_LENGTH)
