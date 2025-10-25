from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.base import create_tables

create_tables()

app = FastAPI(title="Capstone Project team5 API")

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Server is running"}