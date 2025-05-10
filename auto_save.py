import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import subprocess

# 구글 인증 - 환경변수 기반
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_JSON = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_JSON, scopes=SCOPES)
client = gspread.authorize(creds)

# 시트 정보
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
SHEET_NAME = "예측결과"
sheet = client.open_by_key(SPREADSHEET_ID)
worksheet = sheet.worksheet(SHEET_NAME)

# 마지막 회차 읽기 및 +1 계산
existing = worksheet.get_all_records()
last_round = existing[-1]["회차"] if existing else 0
new_round = int(last_round) + 1

# 예측값 (임시 예시)
predictions = ["RIGHT4EVEN", "LEFT3EVEN", "LEFT4ODD"]
prediction_str = " / ".join(predictions)

# 저장
now = datetime.now().strftime("%Y-%m-%d")
row = [now, new_round, "", "", "", prediction_str]
worksheet.append_row(row)

# 학습 자동 실행
subprocess.run(["python", "predict_train.py"])
