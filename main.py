from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from typing import Optional
import soundfile as sf
import io
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from collections import defaultdict
from datetime import datetime
import json
import uuid
import shutil

from database import Base, engine, SessionLocal
from models import User, Detect, ALL
import util
import os
from pydantic import BaseModel



app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists('uploads'):
    os.makedirs('uploads')
    


@app.get("/")
async def root():
    return {"message": "Hello World"}


#월별 데이터 가져오기
@app.get("/getMonthlyData/")
def get_monthly():
    db = SessionLocal()
    Date_data = db.query(Detect.Date).all()
    db.close()

    monthly_counts = defaultdict(int)
    for row in Date_data:
        date = row.Date  # Row 객체에서 Date 속성 추출
        month = date.strftime("%Y-%m")  # 월별 형식으로 변환
        monthly_counts[month] += 1

    return monthly_counts


#일별 데이터 가져오기
@app.get("/getDailyData/")
def get_daily():
    db = SessionLocal()
    Date_data = db.query(Detect.Date).all()
    db.close()

    daily_counts = defaultdict(int)
    for row in Date_data:
        date = row.Date  # Row 객체에서 Date 속성 추출
        day = date.strftime("%Y-%m-%d")  # 일별 형식으로 변환
        daily_counts[day] += 1

    return daily_counts

#피싱 종류별 데이터
@app.get("/labelData/")
def get_label():
    db = SessionLocal()
    Label_data = db.query(Detect.Label).all()
    db.close()

    label_counts = defaultdict(int)

    for label in Label_data:
        label_str = label[0]  # 라벨 데이터는 튜플로 반환되므로 첫 번째 요소를 가져옴
        label_counts[label_str] += 1

    return label_counts

@app.get("/userData")
def get_userdata():
    db = SessionLocal()
    user_data = db.query(User).all()
    db.close()
    return user_data

@app.get("/phishingData")
def get_pishingdata():
    db = SessionLocal()
    pishing_data = db.query(Detect).all()
    db.close()
    return pishing_data


@app.post("/STT")
async def create_upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    wav_data = util.convert_to_wav(contents)
    bytes_io = io.BytesIO(wav_data)
    data, samplerate = sf.read(bytes_io, dtype='float32')
    if data.ndim > 1:
        data = data[:, 0]
    sand_text = util.whisper(data)
    return sand_text



# app에서 파일 업로드를 위한 API
@app.post("/api")
async def upload_file(file: UploadFile = File(...)):
    unique_filename = f"{uuid.uuid4()}-{file.filename}"
    file_path = f"./uploads/{unique_filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": unique_filename}


class TestUser(BaseModel):
    id: str
    pwd: str
    phone: int
    date: datetime


@app.post("/addUser")
async def add_user(user:TestUser):
    print(user)
    return {"message": "User added successfully", "user": user}


# util.gpt('str변수') > GPT 모델 사용하는 함수

# 서버단에서 테스트를 위해서 작성했던 코드
# @app.post("/GPT")
# async def create_gpt_answer(sand_text: str):
#     answer = await util.gpt(sand_text)
#     return answer


# request 에 따른 응답 페이지 로직 예시
# @app.post("/requestUser")
# async def main_check(file: UploadFile = File(...), User_pk: int = Form(...)):
#     sand_text = await create_upload_file(file) # Front(APP)에서 입력받은 파일을 쌓는 로직이 필요함
#     answer = await create_gpt_answer(sand_text)
#     if answer["label"] == "해당없음":
#         return {"result": 0}
#     else:
#         Record = "url"
#         db = SessionLocal()
#         db.add(Detect(Date=datetime.now(), Record=Record, ID=User_pk, Label=answer["label"]))
#         db.commit()
#         db.close()
#         return {"result": 1}