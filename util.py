import io
from pydub import AudioSegment
from transformers import pipeline
from openai import OpenAI



def convert_to_wav(contents):
    file_like_object = io.BytesIO(contents)
    audio = AudioSegment.from_file(file_like_object)
    byte_buffer = io.BytesIO()
    audio.export(byte_buffer, format="wav")
    byte_buffer.seek(0)
    wav_data = byte_buffer.getvalue()
    return wav_data


def whisper(wav):
    pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")
    result = pipe(wav)
    return result["text"]


OPENAI_API_KEY = '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'

async def gpt(query):
    client = OpenAI(api_key=OPENAI_API_KEY)
    model = "gpt-4-turbo-preview"
    head = "당신은 주어진 대화를 통해 보이스피싱 유무를 판단하는 labeler 입니다. 보이스피싱의 label은 [지인사칭, 기관사칭, 해당없음]으로 구성됩니다.\n\n다음은 각 레이블에 대한 예시입니다.\n지인사칭: '안녕하세요. 저는 김영희입니다. 지금 급한 일이 있어서 돈을 빌려주시겠어요?'\n기관사칭: '안녕하세요. 저희 은행에서 전화드립니다. 고객님의 계좌에 문제가 발생했습니다. 확인해주시겠어요?'\n해당없음: '안녕하세요. 오늘은 어떤 일로 전화드린 건가요?'\n\n판단할 대화: '"
    tail = "' 답변은 아래의 JSON Format으로 반환합니다. \n{\n 'label': ''\n}"
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