import json
import os
import requests
import gspread
from datetime import datetime
from google.oauth2 import service_account

# ✅ 환경변수에서 인증 정보 불러오기
service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
creds = service_account.Credentials.from_service_account_info(service_account_info)
client = gspread.authorize(creds)

# ✅ 시트 열기
SPREADSHEET_ID = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
SHEET_NAME = "예측결과"
sheet = client.open_by_key(SPREADSHEET_ID)
worksheet = sheet.worksheet(SHEET_NAME)

print("✅ 시트 열기 성공: 예측결과")

# ✅ 최근 회차 결과 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
data = response.json()

# ✅ 회차 정보 추출
round_num = data["round"]
date = data["date"]
left_right = data["leftRight"]
line = data["line"]
odd_even = data["oddEven"]

# ✅ 중복 저장 방지
existing = worksheet.get_all_records()
if any(str(r["회차"]) == str(round_num) and r["날짜"] == date for r in existing):
    print(f"⚠️ 이미 저장된 회차: {date} {round_num}회차")
else:
    worksheet.append_row([date, round_num, left_right, line, odd_even])
    print(f"✅ 저장 완료: {date} {round_num}회차 → {left_right}, {line}, {odd_even}")
