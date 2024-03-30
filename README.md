# 27CM_finalProject_BE


pip_list.txt에 설치한 패키지 있습니다.


ffmpeg 환경변수 설정 필요합니다.

DB에 더미데이터 저장되어 있습니다.


=====================

API 정의서


APP <-> SERVER		*

![image](https://github.com/AI-X-27CM/27CM_finalProject_BE/assets/131187694/fc292c56-1433-4547-b321-0acb0c5fd4e6)



ADMIN <-> SERVER		*

![image](https://github.com/AI-X-27CM/27CM_finalProject_BE/assets/131187694/2595cff3-bb8d-4666-afa5-c29700faa0bc)



* 사용 모델 / GPT / Whisper / 합성음성감지

* /api  > 음성데이터를 입력 받아서 합성음성감지 모델과 Whisper 모델 전달 > 결과 반환

* GPT > 입력받은 STR 타입의 Text를 프롬프트 문에 전달하여 GPT 요청
