from fastapi import FastAPI
from app.models.user import *
from app.db.database import engine, Base
import app.routers.user as user_routers
import os

if os.environ.get('TESTING', None) != 'True':
    Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_routers.router, tags=["Users"], prefix="/api/users")

@app.get("/")
def root():
    return {"message": "ok"}