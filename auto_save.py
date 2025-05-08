import json
import gspread
from google.oauth2.service_account import Credentials
import requests
from datetime import datetime

# ✅ 환경변수 없이 JSON 파일 직접 불러오기
with open("service_account.json", "r", encoding="utf-8") as f:
    service_account_info = json.load(f)

credentials = Credentials.from_service_account_info(service_account_info)
gc = gspread.authorize(credentials)

# 🔧 구글 시트 정보
SPREADSHEET_KEY = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet("예측결과")

# 🔄 실시간 결과 불러오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
res = requests.get(url)
data = res.json()

# 📌 필요한 데이터 추출
date = data["date"]
round_num = data["round"]
ladder_result = data["result"]  # 예: '좌사홀'

# 📅 시간 정보
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ✅ 시트에 중복 확인 후 저장
values = worksheet.get_all_values()
existing_rounds = [row[1] for row in values[1:]]  # 헤더 제외

if str(round_num) not in existing_rounds:
    worksheet.append_row([now, str(round_num), date, ladder_result])
    print(f"{round_num}회차 저장 완료")
else:
    print(f"{round_num}회차는 이미 저장됨")
