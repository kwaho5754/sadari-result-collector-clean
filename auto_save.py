import os
import json
import gspread
import requests
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# ✅ 환경변수에서 JSON 문자열 불러오기
raw_json = os.environ.get("SERVICE_ACCOUNT_JSON_RAW")
if not raw_json:
    raise Exception("SERVICE_ACCOUNT_JSON_RAW 환경변수가 없습니다.")

# ✅ 줄바꿈 복원
formatted_json = raw_json.replace("\\n", "\n")

# ✅ JSON 유효성 검사
try:
    json.loads(formatted_json)
except json.JSONDecodeError as e:
    raise Exception("환경변수 JSON 형식 오류: " + str(e))

# ✅ service_account.json로 저장
with open("service_account.json", "w") as f:
    f.write(formatted_json)

# ✅ 인증 처리
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
gc = gspread.authorize(credentials)

# ✅ 시트 연결
spreadsheet_id = '1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE'
sheet = gc.open_by_key(spreadsheet_id).worksheet('예측결과')

# ✅ 실시간 데이터 요청
url = 'https://ntry.com/data/json/games/power_ladder/recent_result.json'
response = requests.get(url)
data = response.json()

# ✅ 최신 데이터 선택
if isinstance(data, list) and len(data) > 0:
    result = data[0]
else:
    raise ValueError("데이터 형식이 올바르지 않습니다.")

# ✅ 데이터 파싱
today = result['reg_date']
round_num = int(result['date_round'])
start_point = result['start_point']
line_count = int(result['line_count'])
odd_even = result['odd_even']

# ✅ 중복 확인 후 저장
existing_rounds = sheet.col_values(2)
if str(round_num) in existing_rounds:
    print(f"{round_num}회차는 이미 있음. 저장 건너뜀")
else:
    sheet.append_row([today, round_num, start_point, line_count, odd_even])
    print(f"{round_num}회차 저장 완료")
