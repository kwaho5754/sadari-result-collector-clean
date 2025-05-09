import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import json
from datetime import datetime
import os

# 🔑 로컬 JSON 파일 직접 불러오기
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
gc = gspread.authorize(credentials)

# 🔢 시트 정보
spreadsheet = gc.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4")
worksheet = spreadsheet.worksheet("예측결과")

# 🌐 실시간 JSON 데이터 요청
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
res = requests.get(url)
data = res.json()

# 📦 데이터 파싱
today = datetime.today().strftime("%Y-%m-%d")
latest = data["list"][0]
round_ = latest["round"]
left_right = latest["leftRight"]
line = latest["line"]
odd_even = latest["oddEven"]

# 🧾 현재 시트에 같은 회차가 있는지 확인
values = worksheet.get_all_values()
header, rows = values[0], values[1:]
existing_rounds = [row[1] for row in rows if len(row) >= 2]
if round_ in existing_rounds:
    print(f"{round_}회차는 이미 저장됨")
else:
    # 시트에 새로운 줄 추가
    new_row = [today, round_, left_right, line, odd_even]
    worksheet.append_row(new_row)
    print(f"{round_}회차 저장 완료")
