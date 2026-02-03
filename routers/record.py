from fastapi import APIRouter, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from datetime import datetime
from db.client import db_client
from db.models.users import User
from db.models.records import Record
from db.schema.record import record_schema, records_schema
from db.schema.user import user_schema, users_schema
from bson import ObjectId


router = APIRouter(prefix="/records", tags=['records'])

############## START TIMER ####################
@router.post("/init")
async def init_timer(task_id: str = (Form(...))):
    
    record_db = search_record_db('task_id', task_id) 
    if type(record_db) == Record and record_db.recording:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "This task is still recording time"
        )

    vals = {
        'task_id' : task_id,
        'start' : datetime.now(),
        'recording' : True,
    }
    record_dict = dict(vals)
    try:
        # create record at DB and return id from the record created
        id = db_client.records.insert_one(record_dict).inserted_id
        new_record = record_schema(db_client.records.find_one({'_id': id}))

        return RedirectResponse(
            url= f"/records/{id}",
            status_code = status.HTTP_302_FOUND
        )
    
    except Exception as e:
        return f"Error {e}"
    

############## STOP TIMER ####################
@router.post("/stop")
async def init_timer(id : str = Form(...)):
    
    record_db = search_record_db('_id', ObjectId(id)) 
    if type(record_db) == Record and not record_db.recording:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "This task is already done"
        )

    end_time = datetime.now()
    time_spend = calculate_time(record_db.start, end_time)

    try: 
        db_client.records.update_one(
            {'_id': ObjectId(record_db.id)},
            {
            '$set': {
                'end': end_time,
                'recording': False,
                'time_spend': time_spend
            }
        })

        record_update = record_schema(db_client.records.find_one({'_id': ObjectId(id)}))
        id = record_update["id"]
        return RedirectResponse(
            url=f"/records/{str(id)}",
            status_code= status.HTTP_302_FOUND
        )
    
    except Exception as e:
        return f"Error {e}"


@router.get("/{id}")
async def get_record(id: str):
    
    if type(search_record_db('_id', ObjectId(id))) != Record:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST
        )  

    record_db = search_record_db('_id', ObjectId(id))

    return record_db

@router.get("/")
async def get_record(id: str):
    
    if type(search_record_db('_id', ObjectId(id))) != Record:
        result = search_record_db('_id', ObjectId(id))
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Type != Record %s \n Return from search_record_db: \t%%s" 
            %type(search_record_db('_id', ObjectId(id))) 
            %result
        )  
    
    record_db = search_record_db('_id', ObjectId(id))

    return record_db


################## FUNCTIONS #######################

def search_record_db(key, value):    
    try:
        record = db_client.records.find_one({key: value})
        return Record(**record_schema(record))
    
    except Exception as e:
        return {
            "message" : "This record does not exist",
            "error" : e
                }
    
def calculate_time(start: datetime, end: datetime) -> str:
    """
    Calcula o tempo gasto arredondado para blocos de 15 minutos.
    
    Args:
        start: Datetime de início
        end: Datetime de fim
        
    Returns:
        String no formato "HH:MM" arredondado para blocos de 15min
    """
    if end < start:
        raise ValueError("End time cannot be before Start")

    duration = end - start    
    # Convert to total minutes
    total_minutes = int(duration.total_seconds() / 60)
    
    # Roundig / 15 minutes
    rounded_minutes = round(total_minutes / 15) * 15
    
    # Rollback to hours and minutes hh:mm
    hours = rounded_minutes // 60
    minutes = rounded_minutes % 60
    
    return f"{hours:02d}:{minutes:02d}"