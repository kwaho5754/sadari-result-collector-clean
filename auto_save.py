import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import subprocess

# 구글 인증
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "service_account.json"
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# 시트 정보
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BB0qI9UUDQzE"
SHEET_NAME = "예측결과"
sheet = client.open_by_key(SPREADSHEET_ID)
worksheet = sheet.worksheet(SHEET_NAME)

# 현재 시트 마지막 회차 읽기
existing = worksheet.get_all_records()
last_round = existing[-1]["회차"] if existing else 0
new_round = int(last_round) + 1

# 예측값 (예시)
predictions = ["RIGHT4EVEN", "LEFT3EVEN", "LEFT4ODD"]
prediction_str = " / ".join(predictions)

# 저장
now = datetime.now().strftime("%Y-%m-%d")
row = [now, new_round, "", "", "", prediction_str]
worksheet.append_row(row)

# ✅ 예측 후 자동 학습 실행
subprocess.run(["python", "predict_train.py"])
