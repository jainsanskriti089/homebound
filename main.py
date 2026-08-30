from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from auth import router as auth_router
from db import init_db
import os

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