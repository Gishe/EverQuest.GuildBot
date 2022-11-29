from dataclasses import dataclass
from game.window import EverQuestWindow
from game.guild.guild_tracker import GuildTracker
from utils.config import get_config
from game.dkp.bid_message_parser import parse_bid_message
from game.dkp.entities.bid_message import BidMessageType
from game.dkp.bidding_round import BiddingRound
from integrations.opendkp.opendkp import OpenDkp
from action_queue import enqueue_action

RESTRICT_TO_GUILDIES = get_config('dkp.bidding.restrict_to_guildies', True)

DEFAULT_ROUND_LENGTH = 180

class BiddingManager:
    def __init__(self, eq_window: EverQuestWindow, guild_tracker: GuildTracker, opendkp: OpenDkp):
        self._eq_window = eq_window
        self._opendkp = opendkp
        self._guild_tracker = guild_tracker
        self._bidding_round = BiddingRound()
    
    def _handle_bid_message(self, bid_message):
        if bid_message.message_type == BidMessageType.ENQUEUE_BID_ITEMS:
            # TODO: Restrict to officers in guild only
            if len(bid_message.items) == 0:
                print('Received enqueue bid message, but no items were enqueued.')
                self._eq_window.send_tell_message(
                    bid_message.from_player,
                    'You must provide a list of items to enqueue, separated by ";"')
                return

            self._bidding_round.enqueue_items(bid_message.items)

            print(f'{bid_message.from_player} has enqueued the following items: {bid_message.items}')

        if bid_message.message_type == BidMessageType.START_ROUND:
            # TODO: Restrict to officers in guild only
            if self._bidding_round.is_enabled():
                print(f'{bid_message.from_player} attempted to start a round of bidding, but a round is currently active.')
                self._eq_window.send_tell_message(
                    bid_message.from_player,
                    'A round of bidding is already active. You cannot start a new round.')
                return

            if not self._bidding_round.has_items():
                print(f'{bid_message.from_player} attempted to start a round of bidding, but no items are in the next round.')
                self._eq_window.send_tell_message(
                    bid_message.from_player,
                    'No items are currently queued for bidding. The round has not been started.')
                return
            
            self._bidding_round.start(bid_message.length or DEFAULT_ROUND_LENGTH)

            for message in self._bidding_round.build_start_round_messages():
                self._eq_window.send_tell_message(
                    bid_message.from_player,
                    message)

        if bid_message.message_type == BidMessageType.END_ROUND:
            # TODO: Restrict to officers in guild only
            if not self._bidding_round.is_enabled():
                print(f'{bid_message.from_player} attempted to end a round of bidding, but a round is not active.')
                self._eq_window.send_tell_message(
                    bid_message.from_player,
                    'There is not a round of bidding currently active.')
                return

            for message in self._bidding_round.build_end_round_messages():
                self._eq_window.send_tell_message(
                    bid_message.from_player,
                    message)

            for bid_result in self._bidding_round.end_round():
                # TODO: FEATURE ENHANCEMENT: Commit wins to OpenDKP raid
                # TODO: FEATURE ENHANCEMENT: Commit alt wins to alt bid tracker
                for message in bid_result.build_chat_messages():
                    self._eq_window.send_tell_message(
                        bid_message.from_player,
                        message)

        if bid_message.message_type == BidMessageType.BID_ON_ITEM:
            if not self._bidding_round.is_enabled():
                print(f'{bid_message.from_player} attempted to bid on {bid_message.item} for {bid_message.amount} dkp, but a round is not active.')
                self._eq_window.send_tell_message(
                    bid_message.from_player,
                    'There is not a round of bidding currently active.')
                return

            try:
                self._bidding_round.bid_on_item(
                    bid_message.from_player,
                    bid_message.item,
                    bid_message.amount,
                    bid_message.is_box_bid,
                    bid_message.is_alt_bid)
            except KeyError:
                self._eq_window.send_tell_message(
                    bid_message.from_player,
                    f'{bid_message.item} is not being bid on. Did you spell the name correctly?')

            print(f'{bid_message.from_player} has bid {bid_message.amount} on {bid_message.item}')

        if bid_message.message_type == BidMessageType.BEGIN_RAID:
            # TODO: Restrict to officers in guild only
            self._opendkp.create_raid(bid_message.raid_name)

            # TODO: FEATURE ENHANCEMENT
            # Begin a process which can take DKP ticks on an interval
            # by performing raid dumps. We will want to think about the case
            # where the bot was started later than the raid. Perhaps we could add a
            # parameter to indicate the start time? Regardless, this process
            # should be updating OpenDKP on that interval for a specific amount.
            # e.g. every 30 mintues add 2 DKP for everyone in the raid.
            # Note: As part of this we may want to automatically accept raid invites
            # from officers in the guild.

    def handle_tell_message(self, tell_message):
        # Do not proceed if restrict to guildies enabled and is not a guild member
        if RESTRICT_TO_GUILDIES and not self._guild_tracker.is_a_member(tell_message.from_character):
            # TODO: Log a warning
            return

        # Should we move this logic upstream and subscribe to bid messages only?
        bid_message = parse_bid_message(tell_message)

        if not bid_message:
            return

        enqueue_action(lambda: self._handle_bid_message(bid_message))
