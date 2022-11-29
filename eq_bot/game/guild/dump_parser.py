import csv

from typing import List

from datetime import datetime
from dateutil.parser import parse

from game.guild.entities.guild_dump import GuildDump
from game.guild.entities.guild_member import GuildMember

def parse_guild_member(dump_time: datetime, member_arr: List[str]) -> GuildMember:
    zone = member_arr[6]
    return GuildMember(
        name=member_arr[0],
        level=int(member_arr[1]),
        class_type=member_arr[2],
        rank=member_arr[3],
        is_alt=member_arr[4] == 'A',
        last_seen_on=parse(member_arr[5]),
        zone=zone,
        public_note=member_arr[7],
        last_seen_by_bot=dump_time,
        is_online=zone and len(zone) > 0
    )

def parse_dump_file(dump_time: datetime, filepath: str) -> GuildDump:
    member_entities = []
    with open(filepath, newline='') as guild_dump:
        members = csv.reader(guild_dump, delimiter='\t')
        for member in members:
            member_entities.append(parse_guild_member(dump_time, member))

    return GuildDump(members=member_entities, taken_at=dump_time)
