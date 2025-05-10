import os
import json
import gspread
from datetime import datetime

# 🔐 환경변수에서 서비스 계정 키 로딩
SERVICE_ACCOUNT_INFO = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
SHEET_ID = os.environ["SPREADSHEET_ID"]
SHEET_NAME = os.environ["SHEET_NAME"]

# 📌 구글 시트 인증 및 접속
creds = gspread.service_account_from_dict(SERVICE_ACCOUNT_INFO)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID)
worksheet = sheet.worksheet(SHEET_NAME)

# 📌 마지막 회차 불러오기
existing = worksheet.get_all_records()
last_round = int(existing[-1]["회차"]) if existing else 0
new_round = last_round + 1

# 📌 예측값 예시
predictions = ["RIGHT4EVEN", "LEFT3EVEN", "LEFT4ODD"]
prediction_str = " / ".join(predictions)

# 📌 시트에 저장
now = datetime.now().strftime("%Y-%m-%d")
row = [now, new_round, "", "", "", prediction_str]
worksheet.append_row(row)
