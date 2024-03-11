from fastapi import FastAPI, Depends, HTTPException
from jinja2 import Environment, FileSystemLoader
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import User, Detect, ALL



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()
templates = Environment(loader=FileSystemLoader("frontend"))


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return RedirectResponse(url="http://localhost:3000")


# @app.post("/users/")
# def create_user(user: User.ID, pwd:User.PWD, Phone:User.Phone, db: Session = Depends(get_db)):
#     db.add(User(ID=user, PWD=pwd, Phone=Phone))
#     pass