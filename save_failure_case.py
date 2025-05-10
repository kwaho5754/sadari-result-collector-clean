import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ✅ 구글 시트 인증
SERVICE_ACCOUNT_JSON = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
creds = Credentials.from_service_account_info(
    SERVICE_ACCOUNT_JSON,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
client = gspread.authorize(creds)

# ✅ 시트 ID 및 이름
SPREADSHEET_ID = '1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE'
SHEET_NAME = '예측결과'

# ✅ 시트에서 가장 마지막 줄 데이터 가져오기
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
data = sheet.get_all_values()
header, *rows = data
last_row = rows[-1]
actual = ''.join([last_row[2], last_row[3], last_row[4]]).upper()  # 예: LEFT3ODD

# ✅ 예측 결과 불러오기
with open('predict_result.json', 'r', encoding='utf-8') as f:
    predict_data = json.load(f)

predicted_list = predict_data['results']  # 예측값 3개 리스트
predict_round = predict_data['round']

# ✅ 실제값이 예측값 3개 중에 없는 경우 → 실패 기록 저장
if actual not in predicted_list:
    try:
        with open('failures.json', 'r', encoding='utf-8') as f:
            failures = json.load(f)
    except FileNotFoundError:
        failures = []

    failures.append({
        "timestamp": str(datetime.now()),
        "round": predict_round,
        "actual": actual,
        "predicted": predicted_list
    })

    # 중복 제거
    failures = [dict(t) for t in {tuple(d.items()) for d in failures}]
    with open('failures.json', 'w', encoding='utf-8') as f:
        json.dump(failures, f, indent=2, ensure_ascii=False)

    print(f"❌ 오답 발생 → {actual} 저장됨.")
else:
    print(f"✅ 정답 포함 → {actual} 맞힘.")
