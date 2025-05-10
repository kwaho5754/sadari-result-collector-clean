import os
import json
import requests
import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- 1. 구글 시트 인증 ---
SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")
if not SERVICE_ACCOUNT_JSON:
    raise Exception("환경변수 'SERVICE_ACCOUNT_JSON'이 설정되지 않았습니다.")

service_account_info = json.loads(SERVICE_ACCOUNT_JSON)
scopes = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
gc = gspread.authorize(credentials)

# --- 2. 시트 정보 설정 ---
SPREADSHEET_ID = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
SHEET_NAME = "예측결과"
worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# --- 3. 최근 회차 데이터 가져오기 ---
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
data = response.json()

recent = data['list'][0]
date = recent['date']
round_number = recent['round']
position = recent['position']        # 좌/우
ladder_count = recent['ladderCount'] # 3/4
oddeven = recent['oddEven']          # 홀/짝

# --- 4. 시트에서 이미 저장된 회차인지 확인 ---
existing_data = worksheet.get_all_records()
is_already_saved = any(
    str(row.get('date')) == str(date) and str(row.get('round')) == str(round_number)
    for row in existing_data
)

if is_already_saved:
    print(f"✅ 이미 저장된 회차입니다: {date} - {round_number}회차")
else:
    # --- 5. 새 데이터 추가 ---
    new_row = [date, round_number, position, ladder_count, oddeven]
    worksheet.append_row(new_row)
    print(f"✅ 저장 완료: {new_row}")
