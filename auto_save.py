import gspread
from google.oauth2.service_account import Credentials
import requests
from datetime import datetime

# 구글 시트 인증
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "service_account.json"
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# 시트 정보
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
SHEET_NAME = "예측결과"
sheet = client.open_by_key(SPREADSHEET_ID)
worksheet = sheet.worksheet(SHEET_NAME)

# 데이터 가져오기
DATA_URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(DATA_URL)
data = response.json()

# 최근 회차 데이터
latest = data[-1]
now = latest['reg_date']
new_round = latest['date_round']
a = latest['start_point']
b = int(latest['line_count'])
c = latest['odd_even']

# 시트에 이미 저장된 마지막 회차 확인
existing = worksheet.get_all_records()
saved_rounds = [int(row["회차"]) for row in existing if str(row["날짜"]) == str(now)]
already_exists = new_round in saved_rounds

# 저장되지 않은 경우만 추가
if not already_exists:
    row = [now, new_round, a, b, c]
    worksheet.append_row(row)
    print(f"✅ 저장 완료: {row}")
else:
    print(f"⚠️ 이미 저장된 회차: {new_round}")
