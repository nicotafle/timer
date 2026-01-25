from fastapi import FastAPI
# from pydantic import BaseModel
from routers import record
from db.client import db_client
from db.schema.record import records_schema


app = FastAPI()

app.include_router(record.router)


@app.get("/")
async def get():
    
    records = db_client.records.find()

    return records_schema(records)