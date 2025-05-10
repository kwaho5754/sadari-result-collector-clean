
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import subprocess

# ---------------------- 구글 인증 ----------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "service_account.json"
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# ---------------------- 시트 정보 ----------------------
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
SHEET_NAME = "예측결과"
sheet = client.open_by_key(SPREADSHEET_ID)
worksheet = sheet.worksheet(SHEET_NAME)

# ---------------------- 최신 회차 및 실제 결과 ----------------------
records = worksheet.get_all_records()
last_row = records[-1] if records else {}
new_round = int(last_row.get("회차", 0)) + 1

# 실제 결과는 마지막 줄에서 추출
actual_result = f"{last_row.get('좌우', '')}{last_row.get('줄수', '')}{last_row.get('홀짝', '')}"

# ---------------------- 머신 학습 및 예측 실행 ----------------------
subprocess.run(["python", "predict_train.py"])

# 예측 결과 받아오기 (predict_train.py가 predictions.txt로 저장한다고 가정)
with open("predictions.txt", "r") as f:
    predictions = [line.strip() for line in f.readlines()]

# ---------------------- 시트 저장 ----------------------
now = datetime.now().strftime("%Y-%m-%d")
prediction_str = " / ".join(predictions)
match = "O" if actual_result in predictions else "X"

row = [now, new_round, "", "", "", prediction_str, actual_result, match]
worksheet.append_row(row)
