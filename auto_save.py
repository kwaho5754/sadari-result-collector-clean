import os
import json
import gspread
import requests
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# ✅ 환경변수에서 JSON 문자열 불러오기
raw_json = os.environ.get("SERVICE_ACCOUNT_JSON_RAW")
if not raw_json:
    raise FileNotFoundError("🔐 service_account.json 파일이 없습니다. Render에 환경변수로 JSON을 넣고 실행하세요.")

# ✅ 문자열을 실제 JSON 파일로 저장
with open("service_account.json", "w") as f:
    f.write(raw_json)

# ✅ 시트 인증
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
gc = gspread.authorize(credentials)

# ✅ 시트 연결
spreadsheet_id = '1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE'
sheet = gc.open_by_key(spreadsheet_id).worksheet('예측결과')

# ✅ 실시간 데이터 가져오기
url = 'https://ntry.com/data/json/games/power_ladder/recent_result.json'
response = requests.get(url)
data = response.json()

# ✅ 가장 최신 회차 데이터 사용
if isinstance(data, list) and len(data) > 0:
    result = data[0]
else:
    raise ValueError("예상한 리스트 형식의 데이터가 아닙니다.")

# ✅ 데이터 파싱
today = result['reg_date']
round_num = int(result['date_round'])
start_point = result['start_point']
line_count = int(result['line_count'])
odd_even = result['odd_even']

# ✅ 중복 여부 확인 후 저장
existing_rounds = sheet.col_values(2)
if str(round_num) in existing_rounds:
    print(f"{round_num}회차는 이미 존재함. 저장 건너뜀")
else:
    sheet.append_row([today, round_num, start_point, line_count, odd_even])
    print(f"{round_num}회차 저장 완료")
