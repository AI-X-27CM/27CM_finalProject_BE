from fastapi import FastAPI, File, UploadFile, HTTPException
import soundfile as sf
import io
import util
from pydub import AudioSegment
from datetime import datetime
from transformers import pipeline
import torch
import json

app = FastAPI()

pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3", device="cuda", generate_kwargs = {"language":"korean"})

@app.post("/stt")
async def stt(file: UploadFile = File(...)):
    start = datetime.now()
    contents = await file.read()
    wav_data = util.convert_to_wav(contents)
    bytes_io = io.BytesIO(wav_data)
    data, samplerate = sf.read(bytes_io, dtype='float32')
    if data.ndim > 1:
        data = data[:, 0]
    
    query = util.whisper(data, pipe)
    end = datetime.now()
    print("소요시간: ", end - start)
    return {"text": query}

@app.post("/gpt")
async def gpt(query: str):
    start = datetime.now()
    answer = await util.gpt(query)
    answer = json.loads(answer)
    if answer["label"] == "해당없음":
        gpt_opinion = 0
    else:
        gpt_opinion = 1
    end = datetime.now()
    print("소요시간: ", end - start)
    return {"label": answer["label"], "gpt_opinion": gpt_opinion}

recode = {}

@app.get("/start/{user_pk}")
async def start(user_pk: int):
    global recode
    recode[user_pk] = []  # 각 사용자의 음성 데이터를 저장할 딕셔너리 초기화
    return {"text": f"List initialized successfully for user_pk: {user_pk}"}

@app.post("/wav_upload")
async def wav_upload(user_pk: int, file: UploadFile = File(...)):
    file_contents = await file.read()
    if user_pk not in recode:
        raise HTTPException(status_code=404, detail=f"User with user_pk: {user_pk} not initialized. Call /start/{user_pk} to initialize.")
    recode[user_pk].append(file_contents)
    return {"text": "File uploaded successfully"}

@app.get("/recode/{user_pk}")
async def get_recode(user_pk: int):
    global recode
    if user_pk not in recode or not recode[user_pk]:
        raise HTTPException(status_code=404, detail=f"No audio files uploaded yet for user_pk: {user_pk}")
    
    # 모든 바이트 데이터를 AudioSegment 객체로 변환
    audio_segments = [AudioSegment.from_file(io.BytesIO(data)) for data in recode[user_pk]]
    
    # 모든 AudioSegment 객체를 하나로 합치기
    combined = sum(audio_segments)
    
    # 합쳐진 AudioSegment를 wav 파일로 내보내기
    output_file = f"combined_{user_pk}.wav"  # 유저별로 파일 이름을 다르게 설정
    combined.export(output_file, format="wav")
    
    return {"text": f"File created successfully for user_pk: {user_pk}", "combined_file": output_file}