from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from lightman_ai.core.settings import Settings
from lightman_ai.exceptions import MultipleDateSourcesError


def get_start_date(settings: Settings, yesterday: bool, today: bool, start_date: date | None) -> datetime | None:
    mutually_exclusive_date_fields = [x for x in [start_date, today, yesterday] if x]

    if len(mutually_exclusive_date_fields) > 1:
        raise MultipleDateSourcesError(
            "--today, --yesterday and --start-date are mutually exclusive. Set one at a time."
        )

    if today:
        now = datetime.now(ZoneInfo(settings.TIME_ZONE))
        return datetime.combine(now, time(0, 0), tzinfo=ZoneInfo(settings.TIME_ZONE))
    elif yesterday:
        yesterday_date = datetime.now(ZoneInfo(settings.TIME_ZONE)) - timedelta(days=1)
        return datetime.combine(yesterday_date, time(0, 0), tzinfo=ZoneInfo(settings.TIME_ZONE))
    elif isinstance(start_date, date):
        return datetime.combine(start_date, time(0, 0), tzinfo=ZoneInfo(settings.TIME_ZONE))
    else:
        return None
