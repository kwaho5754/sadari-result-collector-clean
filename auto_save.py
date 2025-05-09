import json
import gspread
from google.oauth2.service_account import Credentials
import requests
from datetime import datetime

# ✅ service_account.json 직접 로딩
with open("service_account.json", "r", encoding="utf-8") as f:
    service_account_info = json.load(f)

credentials = Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

gc = gspread.authorize(credentials)

SPREADSHEET_ID = '1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4'
worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet("예측결과")

url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
res = requests.get(url)
data = res.json()

today = datetime.today().strftime("%Y-%m-%d")
latest = [d for d in data if d['date'] == today][-1]

row = [latest['date'], latest['round'], latest['position'], latest['ladder_count'], latest['odd_even']]
worksheet.append_row(row)
print("✅ 저장 완료:", row)
