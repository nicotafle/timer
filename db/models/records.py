from pydantic import BaseModel, Field
from datetime import datetime


class Record(BaseModel):
    id : str | None = None
    task_id : str 
    start : datetime | None = None
    end : datetime | None = None
    time_spend : str | None = Field(None, description = "Time in blocks os 15 minutes")
    recording : bool = False