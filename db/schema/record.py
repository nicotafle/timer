
def record_schema(record) -> dict:
    if not record:
        return {}
    return {
        "id": str(record["_id"]),
        "start": record.get("start"),
        "end": record.get("end"),
        "pause_at": record.get("pause_at"),
        "last_started_at": record.get("last_started_at"),
        "task_id": record.get("task_id"),
        "recording": record.get("recording", False),
        "paused": record.get("paused", False),
        "accumulated_seconds": record.get("accumulated_seconds", 0),
        "break_time": record.get("break_time"),
        "time_spend": record.get("time_spend"),
        "rounded_time_spend": record.get("rounded_time_spend"),
    }


def records_schema(records) -> list:
    return [record_schema(record) for record in records]
