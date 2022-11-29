from datetime import datetime

from game.guild.entities.dkp_summary import DkpSummary
from game.guild.entities.dkp_summary_differential import DkpSummaryDifferential

from utils.config import get_config


OFF_DUTY_METRIC_KEY=get_config('guild_tracking.opendkp_metrics.off_duty.key')
OFF_DUTY_METRIC_THRESHOLD=get_config('guild_tracking.opendkp_metrics.off_duty.threshold')


def build_differential(from_summary: DkpSummary, to_summary: DkpSummary) -> DkpSummaryDifferential:
    offduty_members = []
    current_time = datetime.now()

    for member in to_summary.guild_members:
        from_member = next((x for x in from_summary.guild_members if x.character_id == member.character_id and x.character_rank != "INACTIVE"), None)
        # If they're below the threshold now, but werent previously
        if from_member and member.__dict__[OFF_DUTY_METRIC_KEY] < OFF_DUTY_METRIC_THRESHOLD and \
            not from_member.__dict__[OFF_DUTY_METRIC_KEY] < OFF_DUTY_METRIC_THRESHOLD:
            offduty_members.append(member)

    return DkpSummaryDifferential(
        offduty_members=offduty_members,
        delta_time=to_summary.taken_at - from_summary.taken_at)
