import json
import os
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# ✅ 환경변수에서 인증 JSON 불러오기
SERVICE_ACCOUNT_JSON = os.environ['SERVICE_ACCOUNT_JSON']
service_account_info = json.loads(SERVICE_ACCOUNT_JSON)
creds = Credentials.from_service_account_info(service_account_info)
client = gspread.authorize(creds)

# ✅ 시트 연결
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
SHEET_NAME = "예측결과"
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# ✅ 마지막 회차 불러오기
records = sheet.get_all_records()
last_round = int(records[-1]["회차"]) if records else 0
new_round = last_round + 1

# ✅ 예측값 준비 (실제 코드는 여기에 예측 결과 삽입)
prediction_str = "RIGHT4EVEN / LEFT3EVEN / LEFT4ODD"
today = datetime.now().strftime("%Y-%m-%d")
row = [today, new_round, "", "", "", prediction_str]

# ✅ 시트에 한 줄 저장
sheet.append_row(row)
