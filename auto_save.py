import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime

# ✅ 환경변수에서 service_account.json 정보 불러오기
service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
gc = gspread.authorize(credentials)

sheet_url = "https://docs.google.com/spreadsheets/d/1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4/edit#gid=0"
sheet = gc.open_by_url(sheet_url).worksheet("예측결과")

# ✅ 실시간 JSON 데이터 요청
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
data = response.json()

# ✅ 회차 정보 추출
round_number = data['round']
date = datetime.now().strftime("%Y-%m-%d")
result = data['result']

# ✅ 결과 시트에 추가
sheet.append_row([date, round_number, result])

print(f"{date} {round_number}회차 저장 완료")
