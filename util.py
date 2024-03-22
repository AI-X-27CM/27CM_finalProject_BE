import io
from pydub import AudioSegment
from transformers import pipeline
from openai import OpenAI
import torch
from pathlib import Path
from datetime import datetime
import os
import librosa
import numpy as np
import soundfile as sf
from io import BytesIO

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")



def convert_to_wav(contents):
    file_like_object = io.BytesIO(contents)
    audio = AudioSegment.from_file(file_like_object)
    byte_buffer = io.BytesIO()
    audio.export(byte_buffer, format="wav")
    byte_buffer.seek(0)
    wav_data = byte_buffer.getvalue()
    return wav_data

# 1. default 값이 무엇인지 모름 >>> 검색하여 확인해보기
def whisper(wav, pipe):
    # pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3", device=0 if torch.cuda.is_available() else -1)
    result = pipe(wav)
    return result["text"]


OPENAI_API_KEY = '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'

async def gpt(query):
    client = OpenAI(api_key=OPENAI_API_KEY)
    model = "gpt-4-turbo-preview"
    head = '''당신은 주어진 문장을 판단하여 보이스피싱 여부를 판단하는 모델입니다.

판단할 문장이 보이스피싱인지 아닌지 판단하고, 보이스피싱이라면 어떤 유형인지 판단해보세요.
label의 유형은 다음과 같습니다.
[지인사칭, 기관사칭, 해당없음]

아래는 각 label에 대한 예시입니다.

1. 지인사칭
-아빠 나 큰일났어 왜 큰일 났어 얼마전에 내가 친국 사체 보증을 서줬는데 어 그랬어? 근데 지금 친구가 연락이 안돼서 내가 사채업자들한테 잡혀왔어 아 진짜로? 어떻게 해줘야돼? 돈 보내줘야돼? 당장 돈을 갚아줘야 풀어준다는데 얼마를 줘야 풀어준대? 3천만원 3천만원? 괜찮아 그정도는 보내줄 수 있어 계좌번호 하나 보내

-여보세요? 어떡해 왜그래? 빨리와 빨리 어디로? 흐흐흑 엄마 여보 침착해 나 성폭행 당했어 누가? 여보? 성폭행 당했어 여보가? 응 어디서? 어디서? 침착해 그사람 그사람 칼 칼들고 칼들고? 어 전화줘봐 소리내지 말고 여보세요 똑똑한 사람이면 나랑 대화를 잘 할테고 바보라면 전화 끊고 당장 신고해 네

2. 기관사칭
- 여보세요. 000 씨 본인 되십니까? 수고 많으십니다. 서울지방남부 경찰청 범죄수익환수에 000 사무관이라고 합니다 네 그런데요다름이 아니라 연락드린 게 성매매특별법 위반 및 불법자금 은닉 건으로 조사 차 연락드렸는데 지금 잠깐 통화 괜찮을까요? 
성매매요? 선생님이 성매매를 했다는 것이 아니라 성매매 집중 단속 중에 선생님 개인정보가 나와서 말씀드린 겁니다.

- 네 고객님 연락드렸던 NH농협은행 대출상담사 이유리에요 네 제가 어떤걸 준비하면 될까요? 네 고객님 제가 몇가지만 여쭤보고 고객님 상황에 맞게끔 한도 이자 산출 도와드려도 괜찮으실까요? 네 고객님 필요하신 자금은 얼마 정도 되세요? 한 1천 5백? 1천 5백만원 되시고 생활 여유자금으로 쓰시고자 하시는 거세요? 네 실례지만 직장인이세요? 사업자세요? 아 지금 실직상태에요 얼마전까지 일용직하다가 실직상태에요 아 휴직상태세요? 휴직상태는 한 달 되셨어요? 일용직 하다가 관뒀으니까 한 달 조금 안됐어요 네 아 그러시면 일용직 하실 때는 급여가 평균으로 어떻게 잡으시면 되세요? 한 2백, 3백? 2백~3백이요? 2백~3백만원 되시고  오늘 까집니까? 기한이? 혹시 지금 바쁘세요? 아니요 말씀하세요 네네 고객님 지금 거주 역은 어디세요? XX구 XX동이요 XX구요 고객님 지금 본인확인차 인증번호 하나 보내드릴 텐데요 고객님 성함을 말씀해 주세요 이거 보이스피싱 아니죠? 네 고객님 당연히 아니죠 XXX XXX 고객님 맞으시죠 네 주민번호 13자리 부탁드립니다 고객님

3. 해당없음
- 여보세요, 여기 OO경찰서인데요. OOO님 맞으신가요? 지갑 잃어버리시지 않으셨나요? 네 분실물이 접수되서 연락드렸습니다.
- 엄마, 18일에 우리 중도금 내는거 있잖아? 5720만원. 이거 조합 명의 농협계좌로 보내라고 안내 우편 왔어. 입금할 때, 동호수 써서 내라네
- 여보세요. 000 씨 본인 되십니까? 수고 많으십니다. 서울지방남부 경찰청 000 이라고 합니다.
- OO은행 입니다. 어떤 업무 떄문에 그러시나요?


판단할 문장: "'''
    tail = '''" 

중요 : 결과는 다음과 같은 json 형태로만 반환합니다.
{"label": label, "phishing_rate":피싱 해당 확률(0~100 사이 정수)}'''
    sanding_message = head + query + tail
    
    messages = [
        {
            "role": "user",
            "content": sanding_message
        }
    ]
    
    response = client.chat.completions.create(model=model, messages=messages, temperature=0, response_format={"type": "json_object"})
    answer = response.choices[0].message.content
    return answer


def combine_and_delete_audio_files(user_pk: int, time: datetime, gpt_opinion: int):
    # 음성 파일을 합치고, 합친 파일을 반환
    # 합친 파일을 반환하기 전에, 합친 파일을 삭제하는 로직을 추가
    time_str = time.strftime("%Y-%m-%d_%H-%M-%S")
    combined_file_path = Path(f"./result/{user_pk}_{time_str}.wav")
    source_folder = Path(f"./uploads/{user_pk}")

    if gpt_opinion == 2:
        os.makedirs(os.path.dirname(combined_file_path), exist_ok=True)
    
        audio_files = sorted(
            [f for f in source_folder.iterdir() if f.is_file() and f.suffix == '.wav'],
            key=lambda x: int(x.stem.split('_')[-1])
        )
        
        combined = AudioSegment.empty()

        for audio_file_path in audio_files:
            audio_segment = AudioSegment.from_file(audio_file_path)
            combined += audio_segment
        # 합친 파일 저장
        combined.export(combined_file_path, format="wav")
    
    # 원본 파일 삭제
    for audio_file_path in source_folder.iterdir():
        if audio_file_path.is_file() and audio_file_path.suffix in ['.wav']:
            audio_file_path.unlink()

    return combined_file_path


def create_mfcc_input_from_wav(wav_file_path, max_pad_length=87, num_mfcc=40):
    # 오디오 파일 로드
    audio, sample_rate = librosa.load(wav_file_path)
    # MFCC 특성 추출
    mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=num_mfcc)
    
    # mfccs의 길이가 max_pad_length보다 길 경우, max_pad_length에 맞게 조정
    if mfccs.shape[1] > max_pad_length:
        mfccs = mfccs[:, :max_pad_length]
    else:
        # 패딩 추가하여 모든 MFCC 배열을 동일한 길이로 맞춤
        pad_width = max_pad_length - mfccs.shape[1]
        mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)), mode='constant')

    # 모델 입력 형태로 재구성 (샘플 수, MFCC 특성 수, MFCC 최대 길이)
    mfccs_input = np.expand_dims(mfccs, axis=0)
    return mfccs_input