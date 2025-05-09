import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ⬇ 환경변수에서 서비스 계정 JSON을 불러와 인증
service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
gc = gspread.authorize(credentials)

# ⬇ 시트 열기
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE/edit?usp=sharing"
doc = gc.open_by_url(spreadsheet_url)
worksheet = doc.worksheet("예측결과")

print("✅ 시트 열기 성공: 예측결과")

# ⬇ 사다리 결과 JSON에서 최근 회차 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
data = response.json()

round_id = data["roundId"]
left_right = data["leftRight"]
line = data["line"]
odd_even = data["oddEven"]
time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ⬇ 이미 저장된 회차인지 확인
existing_rounds = worksheet.col_values(1)
if str(round_id) in existing_rounds:
    print(f"⚠ 이미 저장된 회차입니다: {round_id}")
else:
    # ⬇ 시트에 저장
    worksheet.append_row([round_id, left_right, line, odd_even, time])
    print(f"📥 저장 완료: 회차 {round_id} / 값: {left_right}, {line}, {odd_even}")
