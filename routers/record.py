from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from db.client import db_client
from db.models.records import Record
from db.schema.record import record_schema, records_schema

template = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/records", tags=["records"])


@router.post("/init")
async def init_timer(task_id: str = Form(...)):
    active_record = db_client.records.find_one({"task_id": task_id, "recording": True})
    if active_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is still recording time",
        )

    now = datetime.now()
    payload = {
        "task_id": task_id,
        "start": now,
        "last_started_at": now,
        "recording": True,
        "paused": False,
        "accumulated_seconds": 0,
    }

    try:
        inserted_id = db_client.records.insert_one(payload).inserted_id
        return RedirectResponse(
            url=f"/records/{inserted_id}",
            status_code=status.HTTP_302_FOUND,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating record: {e}",
        )


@router.post("/pause")
async def pause_timer(task_id: str = Form(...)):
    record_db = search_latest_record_db(
        {"task_id": task_id, "recording": True, "end": None},
    )
    if not record_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active record found for this task_id",
        )
    if not record_db.recording:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is paused or already done",
        )
    if not record_db.last_started_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot pause a record without a start timestamp",
        )

    pause_time = datetime.now()
    elapsed_seconds = max(
        0,
        int((pause_time - record_db.last_started_at).total_seconds()),
    )
    accumulated_seconds = record_db.accumulated_seconds + elapsed_seconds

    try:
        db_client.records.update_one(
            {"_id": ObjectId(record_db.id)},
            {
                "$set": {
                    "break_time": format_duration(accumulated_seconds),
                    "pause_at": pause_time,
                    "recording": False,
                    "paused": True,
                    "accumulated_seconds": accumulated_seconds,
                    "last_started_at": None,
                }
            },
        )

        return RedirectResponse(
            url=f"/records/{record_db.id}",
            status_code=status.HTTP_302_FOUND,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error pausing record: {e}",
        )


@router.post("/resume")
async def resume_timer(task_id: str = Form(...)):
    record_db = search_latest_record_db(
        {"task_id": task_id, "paused": True, "recording": False, "end": None},
    )
    if not record_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No paused record found for this task_id",
        )
    if record_db.end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot resume a finished task",
        )
    if record_db.recording:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is already recording",
        )
    if not record_db.paused:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is not paused",
        )

    try:
        db_client.records.update_one(
            {"_id": ObjectId(record_db.id)},
            {
                "$set": {
                    "recording": True,
                    "paused": False,
                    "last_started_at": datetime.now(),
                    "pause_at": None,
                }
            },
        )
        return RedirectResponse(
            url=f"/records/{record_db.id}",
            status_code=status.HTTP_302_FOUND,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resuming record: {e}",
        )


@router.post("/stop")
async def stop_timer(task_id: str = Form(...)):
    record_db = search_latest_record_db(
        {
            "task_id": task_id,
            "end": None,
            "$or": [{"recording": True}, {"paused": True}],
        },
    )
    if not record_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No open record found for this task_id",
        )
    if record_db.end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is already done",
        )
    if not record_db.recording and not record_db.paused:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is not active",
        )

    end_time = datetime.now()
    final_seconds = record_db.accumulated_seconds

    if record_db.recording and record_db.last_started_at:
        elapsed_seconds = max(0, int((end_time - record_db.last_started_at).total_seconds()))
        final_seconds += elapsed_seconds

    try:
        db_client.records.update_one(
            {"_id": ObjectId(record_db.id)},
            {
                "$set": {
                    "end": end_time,
                    "recording": False,
                    "paused": False,
                    "last_started_at": None,
                    "accumulated_seconds": final_seconds,
                    "time_spend": format_duration(final_seconds),
                    "rounded_time_spend": format_duration(round_to_15_min_seconds(final_seconds)),
                }
            },
        )

        return RedirectResponse(
            url=f"/records/{record_db.id}",
            status_code=status.HTTP_302_FOUND,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error stopping record: {e}",
        )


@router.get("/{id}")
async def get_record(id: str, request: Request):
    record_db = search_record_db("_id", parse_object_id(id))
    if not record_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )

    if record_db.recording and not record_db.end and record_db.last_started_at:
        now = datetime.now()
        elapsed = max(0, int((now - record_db.last_started_at).total_seconds()))
        middle_time_spend = format_duration(record_db.accumulated_seconds + elapsed)

        return template.TemplateResponse(
            "record.html",
            {
                "request": request,
                "record": record_db,
                "middle_time_spend": middle_time_spend,
            },
        )

    if record_db.paused and not record_db.end and not record_db.break_time:
        record_db.break_time = format_duration(record_db.accumulated_seconds)

    return template.TemplateResponse(
        "record.html",
        {"request": request, "record": record_db},
    )


@router.get("/")
async def list_records():
    records = db_client.records.find().sort("start", -1)
    return records_schema(records)


def parse_object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid record id",
        )


def search_record_db(key, value):
    try:
        record_db = db_client.records.find_one({key: value})
        if not record_db:
            return None
        return Record(**record_schema(record_db))
    except Exception:
        return None


def search_latest_record_db(filters: dict):
    try:
        record_db = db_client.records.find_one(filters, sort=[("start", -1)])
        if not record_db:
            return None
        return Record(**record_schema(record_db))
    except Exception:
        return None


def format_duration(total_seconds: int) -> str:
    if total_seconds < 0:
        total_seconds = 0
    total_minutes = total_seconds // 60
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"


def round_to_15_min_seconds(total_seconds: int) -> int:
    total_minutes = total_seconds / 60
    rounded_minutes = round(total_minutes / 15) * 15
    return int(rounded_minutes * 60)
