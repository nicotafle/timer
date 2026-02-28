from pydantic import BaseModel, Field
from datetime import datetime


class Record(BaseModel):
    id : int | None = None
    task_id : str 
    start : datetime | None = None
    end : datetime | None = None
    pause_at : datetime | None = None
    break_time : datetime | None = None
    recording : bool = False
    paused : bool = False
    subtotal_spend : str | None
    time_spend : str | None = Field(None, description = "Time in blocks os 15 minutes")