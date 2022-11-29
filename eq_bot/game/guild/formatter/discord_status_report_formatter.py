from game.guild.entities.guild_dump_differential import GuildDumpDifferential
from game.guild.entities.dkp_summary_differential import DkpSummaryDifferential
from game.guild.dump_analyzer import DAYS_UNTIL_INACTIVE

class DiscordStatusReportFormatter:
    def build_output(self, dump_differential: GuildDumpDifferential = None, dkp_summary_differential: DkpSummaryDifferential = None) -> str:
        if (not dump_differential or not dump_differential.has_differences) and \
            (not dkp_summary_differential or not dkp_summary_differential.has_differences):
            return

        minutes = dump_differential.delta_time.total_seconds() / 60
        hours = minutes / 60
        minutes = int(minutes % 60)
        days = int(hours / 24)
        hours = int(hours % 24)

        discord_message = f"__**Guild Status Report**__\n"
        discord_message += f"_{days} days, {hours} hours, and {minutes} minutes since last dump_\n\n"

        if dump_differential:
            if len(dump_differential.new_members) > 0:
                discord_message += f"**Joined**\n"
                discord_message += f"```diff\n"
                for member in dump_differential.new_members:
                    discord_message += f"+ {member.name} - {member.level} {member.class_type} {'(Alt)' if member.is_alt else ''}\n"
                discord_message += "```\n"

            if len(dump_differential.left_members) > 0:
                discord_message += f"**Left**\n"
                discord_message += f"```diff\n"
                for member in dump_differential.left_members:
                    discord_message += f"- {member.name} - {member.level} {member.class_type} {'(Alt)' if member.is_alt else ''}\n"
                discord_message += "```\n"

            if len(dump_differential.inactive_members) > 0:
                discord_message += f"**Inactive ({DAYS_UNTIL_INACTIVE} days in-game)**\n"
                discord_message += f"```fix\n"
                for member in dump_differential.inactive_members:
                    discord_message += f"- {member.name} - {member.level} {member.class_type} {'(Alt)' if member.is_alt else ''}\n"
                discord_message += "```\n"

        if dkp_summary_differential:
            if len(dkp_summary_differential.offduty_members) > 0:
                discord_message += f"**Off Duty (RA < 40%)**\n"
                discord_message += f"```fix\n"
                for member in dkp_summary_differential.offduty_members:
                    discord_message += f"- {member.character_name} - {member.character_class}\n"
                discord_message += "```\n"

        return discord_message + "\n"
