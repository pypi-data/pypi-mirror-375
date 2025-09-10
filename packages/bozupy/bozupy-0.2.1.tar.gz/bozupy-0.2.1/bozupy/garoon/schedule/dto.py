from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, date

from ..constant import EventTypes


@dataclass
class Facility:
    code: str
    id: int
    name: str
    parent_id: int | None = None


@dataclass
class RepeatInfo:
    type: str
    start_time: time | None
    end_time: time | None
    period_start: date
    period_end: date
    day_of_week: int | None
    day_of_month: int | str | None


@dataclass
class GaroonEvent:
    id: int
    subject: str
    creator_code: str
    event_type: EventTypes
    start: datetime | None
    end: datetime | None
    created_at: datetime
    attendee_codes: set[str]
    watcher_codes: set[str]
    facility_codes: set[str] = field(default_factory=set)
    note: str | None = None
    label: str | None = None
    repeat_info: RepeatInfo | None = None
