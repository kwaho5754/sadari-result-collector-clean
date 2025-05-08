import os
import json
import gspread
import requests
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# ✅ 로컬 또는 Render에 존재하는 파일로부터 로드
if not os.path.exists("service_account.json"):
    raise FileNotFoundError("🔒 service_account.json 파일이 없습니다. Render에 직접 업로드하거나 Colab에서 실행하세요.")

with open("service_account.json") as f:
    service_account_info = json.load(f)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
gc = gspread.authorize(credentials)

# ✅ 시트 연결
spreadsheet_id = '1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE'
sheet = gc.open_by_key(spreadsheet_id).worksheet('예측결과')

# ✅ 데이터 가져오기
url = 'https://ntry.com/data/json/games/power_ladder/recent_result.json'
response = requests.get(url)
data = response.json()

# ✅ 리스트 첫 번째 결과 사용
if isinstance(data, list) and len(data) > 0:
    result = data[0]
else:
    raise ValueError("예상한 리스트 구조가 아님")

# ✅ 키 추출
today = result['reg_date']
round_num = int(result['date_round'])
start_point = result['start_point']
line_count = int(result['line_count'])
odd_even = result['odd_even']

# ✅ 중복 체크 후 저장
existing_rounds = sheet.col_values(2)
if str(round_num) in existing_rounds:
    print(f"{round_num}회차는 이미 존재함. 저장 건너뜀")
else:
    sheet.append_row([today, round_num, start_point, line_count, odd_even])
    print(f"{round_num}회차 저장 완료")
