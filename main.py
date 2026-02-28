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
        records = records_schema(db_client.records.find().sort("start", -1))
        response_dict = {"request": request, "records": records}
        return template.TemplateResponse("home.html", response_dict)
    except Exception:
        return template.TemplateResponse("home.html", {"request": request})

@app.get("/start-record")
async def start_record_view(request: Request):
    response = {"request": request, "to_start": True, "to_pause": False, "to_stop": False, "to_resume": False}
    return template.TemplateResponse("home.html", response)

@app.get("/stop-record")
async def stop_record_view(request: Request):
    response = {"request": request, "to_start": False, "to_pause": False, "to_stop": True, "to_resume": False}
    return template.TemplateResponse("home.html", response)

@app.get("/pause-record")
async def pause_record_view(request: Request):
    response = {"request": request, "to_start": False, "to_pause": True, "to_stop": False, "to_resume": False}
    return template.TemplateResponse("home.html", response)

@app.get("/resume-record")
async def resume_record_view(request: Request):
    response = {
        "request": request,
        "to_start": False,
        "to_pause": False,
        "to_stop": False,
        "to_resume": True,
    }
    return template.TemplateResponse("home.html", response)


@app.get("/")
async def get():
    records = db_client.records.find().sort("start", -1)
    return records_schema(records)
