from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
import io
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from collections import defaultdict
import json
from transformers import pipeline
import torch
from datetime import datetime
from pydub import AudioSegment
import os
from tensorflow.keras.models import load_model

from database import Base, engine, SessionLocal
from models import User, Detect, ALL, input_User, error, input_login, input_error, input_gpt
import util

import time as t

# 서버 업로드 시, 폴더 생성 / 음성파일이 저장되는 폴더

# 10초 마다 APP에서 음성파일을 전달받는 폴더
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# 피싱인 경우, 최종 음성파일 저장
if not os.path.exists('result'):
    os.makedirs('result')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# whisper 모델 로드
pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3", device="cuda" if torch.cuda.is_available() else "cpu", generate_kwargs = {"no_repeat_ngram_size": 2, "language":"ko"})
print(util.whisper("start.wav", pipe))
print(util.whisper("1_0.wav", pipe))
loaded_model = load_model('models\your_model_name.h5') # 합성음성 모델 로드

# DB 의존성 주입을 위하여 사용
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 전역 변수 초기화
global_service_on = 0
global_gpt_on = 0
user_voice_data = {}


# 스타팅 포인트 스웨거 연결
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

# 전화가 시작되었을 때, 아래 포인트에 get 요청을 보냄.
@app.get("/start/{user_pk}")
async def start(user_pk: int):
    global global_service_on, global_gpt_on
    global_service_on = 1
    global_gpt_on = 1
    mkdir_path = f"./uploads/{user_pk}"
    if not os.path.exists(mkdir_path):
        os.makedirs(mkdir_path)
    return user_pk

# 전화가 끝났을 때, 아래 엔드 포인트에 get 요청을 보냄
@app.get("/end/{user_pk}/{label}/{gpt_opinion}")
async def end(user_pk: int, label: str, gpt_opinion: int):
    global global_service_on, user_voice_data
    global_service_on = 0

    time = datetime.now()
    combined_file_path = util.combine_and_delete_audio_files(user_pk, time, gpt_opinion) # 피싱이면, 음성파일 저장
    combined_file_path_str = str(combined_file_path)
    
    # DB에 저장
    db = SessionLocal()
    
    if gpt_opinion == 2:
        db.add(Detect(User_pk=user_pk, Label=label, Record=combined_file_path_str, Date=time))
        
    stats = db.query(ALL).first()
    if stats:
        stats.ALL_Cnt += 1
        if gpt_opinion == 1:
            stats.Detect_Cnt += 1
        db.commit()
    db.close()

    # 유저 음성 데이터 초기화
    user_voice_data[user_pk] = []

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

#유저별 데이터
@app.get("/userData")
def get_userdata():
    db = SessionLocal()
    user_data = db.query(User).all()
    db.close()
    return user_data

#피싱 데이터
@app.get("/phishingData")
def get_pishingdata():
    db = SessionLocal()
    pishing_data = db.query(Detect).all()
    db.close()
    return pishing_data


# app에서 음성파일 전달 및 STT 모델 호출
@app.post("/api")
async def upload_file(userNo: int = Form(...), file: UploadFile = File(...)):
    global user_voice_data, global_gpt_on
    if global_gpt_on == 0:
        user_voice_data[userNo] = []
        return "not on call"

    directory_path = f"./uploads/{userNo}"
    existing_files = os.listdir(directory_path)
    count = len(existing_files)
    unique_filename = f"{userNo}_{count}" + ".wav"

    file_path = os.path.join(directory_path, unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    contents = AudioSegment.empty()
    audio_segment = AudioSegment.from_file(file_path)
    contents += audio_segment
    byte_buffer = io.BytesIO()
    contents.export(byte_buffer, format="wav")
    byte_buffer.seek(0)
    wav_data = byte_buffer.getvalue()

    text = util.whisper(wav_data, pipe)

    if userNo not in user_voice_data: # 10 초마다 데이터를 
        user_voice_data[userNo] = []
        user_voice_data[userNo].append(text)
    else:
        user_voice_data[userNo].append(text)

    combined_text = "".join(user_voice_data[userNo]) # STT text 데이터를 합쳐서 반환

    pre_data = util.create_mfcc_input_from_wav(file_path)
    result = loaded_model.predict(pre_data)[0]
    result = result.round(2)
    print(result)
    print(result[0])
    float_result = float(result[0])
    
    if float_result >= 0.99:
        synthesis = 1
    else:
        synthesis = 0

    return {'combined_text': combined_text, 'synthesis': synthesis}

# gpt api 텍스트 데이터를 전달 받아서 {label, gpt판단결과} 로 반환
@app.post("/gpt")
async def gpt(whisper: input_gpt):
    whisper = whisper.dict()
    print(whisper["whisper"])
    global global_gpt_on, global_service_on

    if global_gpt_on == 0:
        return "not on call"
    answer = await util.gpt(whisper["whisper"])
    answer = json.loads(answer)

    gpt_opinion = 0

    if answer["phishing_rate"] >= 10:
        gpt_opinion = 1
    
    if answer["phishing_rate"] > 90:
        gpt_opinion = 2

    if global_service_on == 0:
        global_gpt_on = 0

    print(answer["label"], gpt_opinion)
    if answer["label"]=="지인사칭":
        answer["label"] = "imp"
    
    if answer["label"]=="기관사칭":
        answer["label"] = "inst_imp"
    
    if answer["label"]=="해당없음":
        answer["label"] = "None"

    return {"label": answer["label"], "gpt_opinion": gpt_opinion}


# stt api 음성데이터를 전달 받아서 text로 반환
# @app.post("/stt/")
# async def stt(userNo: int = Form(...), file: UploadFile = File(...)):
#     contents = await file.read()
#     wav_data = util.convert_to_wav(contents)
#     bytes_io = io.BytesIO(wav_data)
#     data, samplerate = sf.read(bytes_io, dtype='float32')
#     if data.ndim > 1:
#         data = data[:, 0]

#     text = util.whisper(data, pipe)
#     global user_voice_data

#     user_voice_data[userNo].append(text)

#     combined_text = "".join(user_voice_data[userNo])

#     return combined_text

# 회원가입 유저 정보 DB 저장
@app.post("/addUser")
async def add_user(user:input_User):
    db = SessionLocal()
    try:
        db.add(User(ID=user.id, PWD=user.pwd, Phone=user.phone, Date=user.date))
        db.commit()
        db.close()
        return {"message": "User added successfully", "user": user}
    except:
        db.close()
        raise HTTPException(status_code=400, detail="User already exists")


@app.delete("/phishingData/{Detect_pk}")
def delete_phishing_data(Detect_pk: int, db: Session = Depends(get_db)):
    item_to_delete = db.query(Detect).filter(Detect.Detect_pk == Detect_pk).first()
    if item_to_delete:
        db.delete(item_to_delete)
        db.commit()
        return {"message": "삭제되었습니다"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")



@app.get("/errorData")
async def get_error_data(db: Session = Depends(get_db)):
    error_data = db.query(error).all()
    formatted_data = {}
    for item in error_data:
        error_time = item.Date.strftime('%H시')
        if error_time not in formatted_data:
            formatted_data[error_time] = {}
        formatted_data[error_time][item.error] = formatted_data[error_time].get(item.error, 0) + 1
    return formatted_data

@app.get("/errorlog")
async def get_error_log(db: Session = Depends(get_db)):
    error_data = db.query(error).all()
    return error_data


@app.post("/error")
async def add_error(input_error: input_error):
    db = SessionLocal()
    db.add(error(error=input_error.error, Date=datetime.now()))
    db.commit()
    db.close()
    return {"message": "error added successfully"}


@app.post("/login")
async def login(user: input_login, db: Session = Depends(get_db)):
    user_data = db.query(User).filter(User.ID == user.id).first()
    if user_data is None:
        return "User not found"
    if user_data.PWD != user.pwd:
        return "Password incorrect"
    return user_data.User_pk