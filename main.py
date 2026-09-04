from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from auth import router as auth_router
from db import init_db
import os

import logging
logging.basicConfig(
    level=logging.INFO, 
    formal="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("homebound.log"),
        logging.StreamHandler(),
    ],
)

print("CWD:", os.getcwd())
print("CLIENT_ID:", repr(os.getenv("TESLA_CLIENT_ID")))
print("REDIRECT_URI:", repr(os.getenv("TESLA_REDIRECT_URI")))

load_dotenv()
init_db()
app = FastAPI()
app.include_router(auth_router)

@app.get("/")
def root():
    return {"status": "homebound backend is running"}

from scheduler import start_scheduler

@app.on_event("startup")
async def on_startup():
    start_scheduler()

from dashboard import router as dashboard_router
app.include_router(dashboard_router)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/dashboard")
def dashboard():
    return FileResponse("static/dashboard.html")