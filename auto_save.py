import json
import os
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
import requests

# 🔐 환경변수 기반 인증
SERVICE_ACCOUNT_JSON = os.environ['SERVICE_ACCOUNT_JSON']
service_account_info = json.loads(SERVICE_ACCOUNT_JSON)
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
client = gspread.authorize(creds)

# 📊 시트 설정
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
SHEET_NAME = "예측결과"
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# 🌐 최근 결과 JSON에서 데이터 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
data = response.json()

# 결과 정보 추출
round_info = data["row"]
game_date = round_info["date"]
round_num = int(round_info["round"])
ladder_side = round_info["result"]["ladder"]     # LEFT / RIGHT
line_count = round_info["result"]["count"]       # 3 / 4
odd_even = round_info["result"]["odd_even"]      # ODD / EVEN

# 🔁 이미 저장된 회차인지 확인
existing = sheet.get_all_records()
last_saved = int(existing[-1]["회차"]) if existing else 0

# ✅ 새로운 회차만 저장
if round_num > last_saved:
    row = [game_date, round_num, ladder_side, line_count, odd_even]
    sheet.append_row(row)
