import gspread
import json
import os
from datetime import datetime

# ✅ 환경변수 기반 인증
from google.oauth2.service_account import Credentials
SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON")
SERVICE_ACCOUNT_INFO = json.loads(SERVICE_ACCOUNT_JSON)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
client = gspread.authorize(creds)

# ✅ 시트 정보
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BB0qI9UUDQzE"
SHEET_NAME = "예측결과"
sheet = client.open_by_key(SPREADSHEET_ID)
worksheet = sheet.worksheet(SHEET_NAME)

# ✅ 현재 시트의 마지막 회차 + 1
existing = worksheet.get_all_records()
last_round = existing[-1]["회차"] if existing else 0
new_round = int(last_round) + 1

# ✅ 예측값 (임시 값 — 실제 예측값은 추후 predict_train.py에서 가져오도록 설정 가능)
predictions = ["RIGHT4EVEN", "LEFT3EVEN", "LEFT4ODD"]
prediction_str = " / ".join(predictions)

# ✅ 시트에 저장할 행 구성
now = datetime.now().strftime("%Y-%m-%d")
row = [now, new_round, "", "", "", prediction_str]
worksheet.append_row(row)

# (선택) ✅ 추후 자동 학습 연동할 경우 아래만 주석 해제
# import subprocess
# subprocess.run(["python", "predict_train.py"])
