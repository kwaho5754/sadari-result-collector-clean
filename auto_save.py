import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import subprocess

# ▶ 구글 인증 (환경변수 없이 json 직접 불러옴)
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "service_account.json"
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
client = gspread.authorize(creds)

# ▶ 시트 정보
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
SHEET_NAME = "예측결과"
sheet = client.open_by_key(SPREADSHEET_ID)
worksheet = sheet.worksheet(SHEET_NAME)

# ▶ 현재 마지막 회차 불러오기
existing = worksheet.get_all_records()
last_row = existing[-1] if existing else {}
last_round = int(last_row.get("회차", 0)) if str(last_row.get("회차", "0")).isdigit() else 0
new_round = last_round + 1

# ▶ 이전 예측값 불러오기 (중복 방지용)
previous_prediction = last_row.get("예측값", "") if last_row else ""

# ▶ 예측 수행 (자동학습 포함)
subprocess.run(["python", "predict_train.py"])

# ▶ 예측값 예시 (실제로는 predict_train.py에서 반환되도록 구성 가능)
predictions = ["RIGHT4EVEN", "LEFT3EVEN", "LEFT4ODD"]
prediction_str = " / ".join(predictions)

# ▶ 예측 결과 중복 여부 판단 후 저장
if prediction_str != previous_prediction:
    today = datetime.now().strftime("%Y-%m-%d")
    row = [today, new_round, "", "", "", prediction_str]
    worksheet.append_row(row)
