import json
import os
import requests
import gspread
from datetime import datetime
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
creds = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
client = gspread.authorize(creds)

SPREADSHEET_ID = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
SHEET_NAME = "예측결과"
sheet = client.open_by_key(SPREADSHEET_ID)
worksheet = sheet.worksheet(SHEET_NAME)

print("✅ 시트 열기 성공: 예측결과")

# ✅ 응답 데이터 불러오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
data = response.json()

# ✅ 가장 최근 결과 1개 사용
result = data[0]

# ✅ 필드 이름에 맞게 수정
round_num = result["date_round"]
date = result["reg_date"]
left_right = result["start_point"]
line = result["line_count"]
odd_even = result["odd_even"]

# ✅ 중복 저장 방지
existing = worksheet.get_all_records()
if any(str(r["회차"]) == str(round_num) and r["날짜"] == date for r in existing):
    print(f"⚠️ 이미 저장된 회차: {date} {round_num}회차")
else:
    worksheet.append_row([date, round_num, left_right, line, odd_even])
    print(f"✅ 저장 완료: {date} {round_num}회차 → {left_right}, {line}, {odd_even}")
