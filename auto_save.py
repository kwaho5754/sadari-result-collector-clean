import gspread
import os
import json
from datetime import datetime

# ✅ 구글 인증 (환경변수 기반)
service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
creds = gspread.service_account_from_dict(service_account_info)
client = gspread.authorize(creds)

# ✅ 시트 정보
SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
SHEET_NAME = os.environ["SHEET_NAME"]
sheet = client.open_by_key(SPREADSHEET_ID)
worksheet = sheet.worksheet(SHEET_NAME)

# ✅ 마지막 회차 불러오기
existing = worksheet.get_all_records()
last_round = int(existing[-1]["회차"]) if existing else 0
new_round = last_round + 1

# ✅ 예측 결과 (임시값 → 실제로는 모델 예측 결과를 대입)
predictions = ["RIGHT4EVEN", "LEFT3EVEN", "LEFT4ODD"]
prediction_str = " / ".join(predictions)

# ✅ 현재 날짜
now = datetime.now().strftime("%Y-%m-%d")

# ✅ 한 줄로 결과 저장
row = [now, new_round, "", "", "", prediction_str]
worksheet.append_row(row)

print(f"✅ 저장 완료: {now} - {new_round}회차 → {prediction_str}")
