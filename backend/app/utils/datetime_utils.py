from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


def ensure_tz(dt: datetime, timezone: str = "UTC") -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo(timezone))
    return dt


def combine_local(day: date, t: time, timezone: str) -> datetime:
    return datetime.combine(day, t).replace(tzinfo=ZoneInfo(timezone))


def daterange(start_date: date, end_date: date):
    day = start_date
    while day <= end_date:
        yield day
        day += timedelta(days=1)


def round_up_to_slot(dt: datetime, slot_minutes: int = 15) -> datetime:
    delta = (slot_minutes - (dt.minute % slot_minutes)) % slot_minutes
    rounded = dt.replace(second=0, microsecond=0)
    if delta:
        rounded += timedelta(minutes=delta)
    return rounded


def utc_now_naive() -> datetime:
    """Zwraca bieżący czas UTC bez informacji o strefie czasowej."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_utc_naive(dt: datetime) -> datetime:
    """Konwertuje datetime do UTC i usuwa tzinfo."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Jeśli nie ma tzinfo, zakładamy UTC
        return dt
    # Konwertuj do UTC i usuń tzinfo
    return dt.astimezone(timezone.utc).replace(tzinfo=None)
