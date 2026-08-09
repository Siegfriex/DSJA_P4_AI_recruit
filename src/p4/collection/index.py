from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndexScope:
    start_month: str
    end_month: str
    operation_names: tuple[str, ...] = (
        "CalendarScreen_ActivityCalendarEntries",
        "CalendarScreen_Activities",
    )

    def validate(self) -> None:
        if self.start_month > self.end_month:
            raise ValueError("INDEX_SCOPE_REVERSED")
