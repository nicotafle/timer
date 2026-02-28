from fastapi import FastAPI, Request
# from pydantic import BaseModel
from routers import record
from db.client import db_client
from db.schema.record import records_schema
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.include_router(record.router)

template = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/home")
async def home(request: Request):
    try:
        records = db_client.records.find()
        response_dict = {"records" : records}
        return template.TemplateResponse(request, "home.html", dict(response_dict))
    except:
        return template.TemplateResponse(request, "home.html")

@app.get("/start-record")
async def start_record(request: Request):
    response = {'to_start': True,
                'to_pause': False,
                'to_stop': False}
    return template.TemplateResponse(request, "home.html", dict(response))

@app.get("/stop-record")
async def start_record(request: Request):
    response = {'to_start': False,
                'to_pause': False,
                'to_stop': True}
    return template.TemplateResponse(request, "home.html", dict(response))

@app.get("/pause-record")
async def start_record(request: Request):
    response = {'to_start': False,
                'to_pause': True,
                'to_stop': False}
    return template.TemplateResponse(request, "home.html", dict(response))


@app.get("/")
async def get():
    
    records = db_client.records.find()

    return records_schema(records)