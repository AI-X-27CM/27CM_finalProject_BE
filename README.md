# 27CM_finalProject_BE


pip_list.txt에 설치한 패키지 있습니다.


ffmpeg 환경변수 설정 필요합니다.

DB에 더미데이터 저장되어 있습니다.


=====================

API 정의서


APP <-> SERVER		*
API종류	API	역할
POST	/login	로그인
POST	/addUser	회원가입
POST	/api	녹음 파일 전달
POST	/gpt	GPT 모델에 text파일 전달
GET	/start	통화 버튼 trigger
GET	/end	통화 종료 버튼 trigger
POST	/error	발생된 에러 전달
![image](https://github.com/AI-X-27CM/27CM_finalProject_BE/assets/131187694/fc292c56-1433-4547-b321-0acb0c5fd4e6)



ADMIN <-> SERVER		*
GET	/getMonthlyData	DB에서 월별 피싱 수 시각화를 위한 데이터 불러오기
GET	/getDailyData	DB에서 일별 피싱 수 시각화를 위한 데이터 불러오기
GET	/labelData	DB에서 보이스피싱 종류별 시각화를 위한 데이터 불러오기
GET	/userData	DB에서 유저 정보 데이터 불러오기
GET	/phishingData	DB에서 보이스피싱으로 확인되었던 통화 데이터를 불러오기
DELETE	/phishingData/{Detect_pk}	DB에 저장된 피싱데이터를 삭제
GET	/errorData	DB에서 에러 데이터 시각화를 위한 데이터 불러오기
GET	/errorlog	DB에서 에러 로그 정보 불러오기
![image](https://github.com/AI-X-27CM/27CM_finalProject_BE/assets/131187694/2595cff3-bb8d-4666-afa5-c29700faa0bc)
