import json
import os
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# ✅ 환경변수에서 JSON 정보 읽기
SERVICE_ACCOUNT_JSON = os.environ['SERVICE_ACCOUNT_JSON']
service_account_info = json.loads(SERVICE_ACCOUNT_JSON)

# ✅ 범위 명확하게 설정
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
client = gspread.authorize(creds)

# ✅ 시트 정보
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
SHEET_NAME = "예측결과"
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# ✅ 마지막 회차 +1
records = sheet.get_all_records()
last_round = int(records[-1]["회차"]) if records else 0
new_round = last_round + 1

# ✅ 예측값 예시
today = datetime.now().strftime("%Y-%m-%d")
prediction_str = "RIGHT4EVEN / LEFT3EVEN / LEFT4ODD"
row = [today, new_round, "", "", "", prediction_str]

# ✅ 시트에 저장
sheet.append_row(row)
