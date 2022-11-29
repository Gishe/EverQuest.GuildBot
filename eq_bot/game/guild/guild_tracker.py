import time
import random
from datetime import datetime, timedelta
from threading import Thread
from dataclasses import dataclass
from game.window import EverQuestWindow, EVERQUEST_ROOT_FOLDER
from game.guild.entities.dkp_summary import DkpSummary
from game.guild.dump_parser import parse_dump_file
from game.guild.dump_analyzer import build_differential as build_dump_differential
from game.guild.dkp_analyzer import build_differential as build_dkp_summary_differential
from game.guild.formatter.discord_status_report_formatter import DiscordStatusReportFormatter
from game.guild.dkp_gateway import DkpGateway
from integrations.discord import send_message, DiscordWebhookType
from utils.file import move_file, make_directory, get_files_from_directory, read_json, write_json
from utils.config import get_config
from utils.array import contains

# TODO: Move to configuration file
DUMP_EXTENSION='.dump'
DUMP_OUTPUT_FOLDER='output\\dumps\\guild'
DUMP_TIME_FORMAT='%Y%m%d-%H%M%S'
DKP_SUMMARY_OUTPUT_FOLDER='output\\dkp\\summary'
DKP_SUMMARY_EXTENSION='.json'
INTERVAL=get_config('guild_tracking.interval', 300)
OUTPUT_TO_DISCORD=get_config('guild_tracking.output_to_discord')
IN_GAME_DUMP_ENABLED=get_config('guild_tracking.in_game_dump.enabled')
DKP_SUMMARY_ENABLED=get_config('guild_tracking.open_dkp.enabled')

class GuildTracker(Thread):
    def __init__(self, eq_window: EverQuestWindow, daemon: bool = True):
        super().__init__(daemon=daemon)
        make_directory(DUMP_OUTPUT_FOLDER)
        make_directory(DKP_SUMMARY_OUTPUT_FOLDER)
        self._eq_window = eq_window
        self._last_dump = self._lookup_most_recent_dump() if IN_GAME_DUMP_ENABLED else None
        self._last_dkp_summary = self._lookup_most_recent_dkp_summary() if DKP_SUMMARY_ENABLED else None
        self._discord_formatter = DiscordStatusReportFormatter()
        self._dkp_gateway = DkpGateway()

    def _get_safe_guild_name(self):
        return self._eq_window.player.guild.replace(' ', '-')

    def _lookup_most_recent_dump(self):
        previous_dump_files = get_files_from_directory(DUMP_OUTPUT_FOLDER, DUMP_EXTENSION)
        previous_dumps = []
        for dump_file in previous_dump_files:
            dump_time = datetime.strptime(dump_file, f"{self._get_safe_guild_name()}-Dump-{DUMP_TIME_FORMAT}{DUMP_EXTENSION}")
            previous_dumps.append(parse_dump_file(dump_time, f"{DUMP_OUTPUT_FOLDER}\{dump_file}"))
        previous_dumps.sort(key=lambda x: x.taken_at, reverse=True)
        return None if not previous_dumps else previous_dumps[0]

    def _lookup_most_recent_dkp_summary(self):
        previous_dkp_summary_files = get_files_from_directory(DKP_SUMMARY_OUTPUT_FOLDER, DKP_SUMMARY_EXTENSION)
        previous_dkp_summaries = []
        for dkp_summary_file in previous_dkp_summary_files:
            taken_at = datetime.strptime(dkp_summary_file, f"DKP-Summary-{self._get_safe_guild_name()}-{DUMP_TIME_FORMAT}{DKP_SUMMARY_EXTENSION}")
            previous_dkp_summaries.append(DkpSummary.from_json(read_json(f"{DKP_SUMMARY_OUTPUT_FOLDER}\{dkp_summary_file}")))
        previous_dkp_summaries.sort(key=lambda x: x.taken_at, reverse=True)
        return None if not previous_dkp_summaries else previous_dkp_summaries[0]

    def _create_dkp_summary(self):
        dkp_summary_time = datetime.now()
        new_dkp_summary = self._dkp_gateway.fetch_dkp_summary()

        dkp_summary_differential = None
        if self._last_dkp_summary:
            dkp_summary_differential = build_dkp_summary_differential(self._last_dkp_summary, new_dkp_summary)
            dkp_summary_differential.print()
            pass
        
        self._last_dkp_summary = new_dkp_summary

        dkp_summary_time_str = dkp_summary_time.strftime(DUMP_TIME_FORMAT)
        dkp_summary_file_name = f"DKP-Summary-{self._get_safe_guild_name()}-{dkp_summary_time_str}{DKP_SUMMARY_EXTENSION}"
        write_json(new_dkp_summary.to_json(), f"{DKP_SUMMARY_OUTPUT_FOLDER}\\{dkp_summary_file_name}")

        return dkp_summary_differential

    def _create_dump(self):
        dump_time = datetime.now()
        dump_time_str = dump_time.strftime(DUMP_TIME_FORMAT)
        dump_filename = f"{self._get_safe_guild_name()}-Dump-{dump_time_str}"
        self._eq_window.guild_dump(dump_filename)
        dump_filepath = f"{EVERQUEST_ROOT_FOLDER}\{dump_filename}.txt"

        new_dump = parse_dump_file(dump_time, dump_filepath)
        new_dump.print()

        dump_differential = None
        if self._last_dump:
            dump_differential = build_dump_differential(self._last_dump, new_dump)
            dump_differential.print()

        self._last_dump = new_dump

        # Backup file in local output for future parsing
        move_file(dump_filepath, f"{DUMP_OUTPUT_FOLDER}\{dump_filename}{DUMP_EXTENSION}")

        return dump_differential

    # Run this as a daemon so the thread will be cleaned up if the process is destroyed
    def run(self) -> None:
        while True:
            self._eq_window.handle_window_action(self.update_status)
            time.sleep(INTERVAL)

    def update_status(self):
        dump_differential = None
        dkp_summary_differential = None

        if IN_GAME_DUMP_ENABLED:
            dump_differential = self._create_dump()

        if DKP_SUMMARY_ENABLED:
            dkp_summary_differential = self._create_dkp_summary()
        
        if OUTPUT_TO_DISCORD:
            message = self._discord_formatter.build_output(
                dump_differential,
                dkp_summary_differential)

            if message:
                send_message(
                    DiscordWebhookType.GUILD_STATUS,
                    message)

    def is_a_member(self, name):
        if not self._last_dump:
            raise ValueError("Last dump has not yet been taken.")
        
        # TODO: Change self.members structure so that we can more easily lookup by name..
        return contains(self._last_dump.members, lambda member: member.name.lower() == name.lower())
