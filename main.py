from fastapi import FastAPI, File, UploadFile
from typing import Optional
import soundfile as sf
import io
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from collections import defaultdict
import json
import uuid
import shutil
from transformers import pipeline

from database import Base, engine, SessionLocal
from models import User, Detect, ALL, input_User
import util

import os
from pydantic import BaseModel

if not os.path.exists('uploads'):
    os.makedirs('uploads')



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# whisper 모델 로드
pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3", device="cuda")
print(util.whisper("start.wav"))

# 전역 변수 초기화
global_service_on = 0

# https://www.uvicorn.org/settings/ 참조

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

# 전화가 시작되었을 때, 아래 포인트에 get 요청을 보냄.
@app.get("/start")
async def start():
    global global_service_on
    global_service_on = 1
    return {"message": "call start"}

# 전화가 끝났을 때, 아래 엔드 포인트에 get 요청을 보냄
@app.get("/end")
async def end():
    global global_service_on
    global_service_on = 0
    # 데이터베이스에 정보를 저장하는 로직을 추가
    return {"message": "call end"}

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


# app에서 파일 업로드를 위한 API
@app.post("/api")
async def upload_file(file: UploadFile = File(...)):
    unique_filename = f"{uuid.uuid4()}-{file.filename}"
    file_path = f"./uploads/{unique_filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"file_path": file_path}

# gpt api 텍스트 데이터를 전달 받아서 {label, gpt판단결과} 로 반환
@app.post("/gpt")
async def gpt(query: str):
    answer = await util.gpt(query)
    answer = json.loads(answer)
    if answer["label"] == "해당없음":
        gpt_opinion = 0
    else:
        gpt_opinion = 1
    return {"label": answer["label"], "gpt_opinion": gpt_opinion}

# stt api 음성데이터를 전달 받아서 text로 반환
@app.post("/stt")
async def stt(file: UploadFile = File(...)):
    contents = await file.read()
    wav_data = util.convert_to_wav(contents)
    bytes_io = io.BytesIO(wav_data)
    data, samplerate = sf.read(bytes_io, dtype='float32')
    if data.ndim > 1:
        data = data[:, 0]
    query = util.whisper(data, pipe)
    return {"text": query}

# 회원가입 유저 정보 DB 저장
@app.post("/addUser")
async def add_user(user:input_User):
    db = SessionLocal()
    db.add(User(ID=user.id, PWD=user.pwd, Phone=user.phone, Date=user.date))
    db.commit()
    db.close()
    return {"message": "User added successfully", "user": user}

