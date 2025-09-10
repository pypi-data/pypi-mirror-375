from datetime import datetime, time, date

from .dto import GaroonEvent, Facility, RepeatInfo
from ..constant import EventTypes
from ...util import str_to_datetime, str_to_time, str_to_date


def _day_of_week_to_int(day_of_week_str: str) -> int | None:
    mapping: dict[str, int] = {
        "MON": 1,
        "TUE": 2,
        "WED": 3,
        "THU": 4,
        "FRI": 5,
        "SAT": 6,
        "SUN": 0
    }
    return mapping.get(day_of_week_str.upper())


def to_event(event_json: dict) -> GaroonEvent:
    event_type: EventTypes = EventTypes.from_str(event_json["eventType"])
    if event_type is EventTypes.REPEATING:
        start: datetime | None = None
        end: datetime | None = None
        repeat_info_json: dict = event_json["repeatInfo"]
        period_start: date = str_to_date(repeat_info_json["period"]["start"])
        period_end: date = str_to_date(repeat_info_json["period"]["end"])
        start_time: time | None = None
        end_time: time | None = None
        if "time" in repeat_info_json:
            if "start" in repeat_info_json["time"] and repeat_info_json["time"]["start"]:
                start_time = str_to_time(repeat_info_json["time"]["start"])
            if "end" in repeat_info_json["time"] and repeat_info_json["time"]["end"]:
                end_time = str_to_time(repeat_info_json["time"]["end"])
        repeat_info: RepeatInfo | None = RepeatInfo(
            type=repeat_info_json["type"],
            start_time=start_time,
            end_time=end_time,
            period_start=period_start,
            period_end=period_end,
            day_of_week=_day_of_week_to_int(repeat_info_json.get("dayOfWeek", "")),
            day_of_month=repeat_info_json.get("dayOfMonth", None)
        )
    else:
        start = str_to_datetime(event_json["start"]["dateTime"])
        end = str_to_datetime(event_json["end"]["dateTime"]) if "end" in event_json and event_json["end"] else None
        repeat_info = None
    return GaroonEvent(
        id=int(event_json["id"]),
        subject=event_json["subject"],
        creator_code=event_json["creator"]["code"],
        event_type=EventTypes.from_str(event_json["eventType"]),
        start=start,
        end=end,
        created_at=str_to_datetime(event_json["createdAt"]),
        attendee_codes=set([attendee["code"] for attendee in event_json.get("attendees", [])]),
        watcher_codes=set([watcher["code"] for watcher in event_json.get("watchers", [])]),
        facility_codes=set([facility["code"] for facility in event_json.get("facilities", [])]),
        note=event_json.get("note", None),
        label=event_json.get("label", None),
        repeat_info=repeat_info
    )


def to_facility(facility_json: dict) -> Facility:
    return Facility(
        code=facility_json["code"],
        id=int(facility_json["id"]),
        name=facility_json["name"],
        parent_id=int(facility_json["parentId"]) if "parentId" in facility_json else None
    )
