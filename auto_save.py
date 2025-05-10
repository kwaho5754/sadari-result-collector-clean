import gspread
import json
import os
from datetime import datetime

# 구글 인증: 환경변수에서 JSON을 직접 불러옴
SERVICE_ACCOUNT_JSON = os.environ['SERVICE_ACCOUNT_JSON']
creds = json.loads(SERVICE_ACCOUNT_JSON)
client = gspread.service_account_from_dict(creds)

# 시트 설정
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
SHEET_NAME = "예측결과"
sheet = client.open_by_key(SPREADSHEET_ID)
worksheet = sheet.worksheet(SHEET_NAME)

# 예측값 예시 (임시값, 실제론 분석 결과로 교체 예정)
predictions = ["RIGHT4EVEN", "LEFT3EVEN", "LEFT4ODD"]
prediction_str = " / ".join(predictions)

# 시트에서 마지막 회차 확인
existing = worksheet.get_all_records()
last_round = int(existing[-1]['회차']) if existing else 0
new_round = last_round + 1

# 현재 날짜
now = datetime.now().strftime("%Y-%m-%d")

# 시트에 저장
row = [now, new_round, "", "", prediction_str]
worksheet.append_row(row)
