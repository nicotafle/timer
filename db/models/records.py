from pydantic import BaseModel, Field
from datetime import datetime


class Record(BaseModel):
    id: str | None = None
    task_id: str
    start: datetime | None = None
    end: datetime | None = None
    pause_at: datetime | None = None
    last_started_at: datetime | None = None
    recording: bool = False
    paused: bool = False
    accumulated_seconds: int = 0
    break_time: str | None = None
    time_spend: str | None = Field(None, description="Real worked time in HH:MM")
    rounded_time_spend: str | None = Field(
        None,
        description="Worked time rounded to 15-minute blocks in HH:MM",
    )
