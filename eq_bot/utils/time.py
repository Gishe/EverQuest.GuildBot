from datetime import datetime, timezone, timedelta

LOCAL_TIMEZONE = datetime.now(timezone(timedelta(0))).astimezone().tzinfo

def local_datetime():
    return datetime.now(LOCAL_TIMEZONE)
