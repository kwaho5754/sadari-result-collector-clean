import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 🔐 구글 인증 정보
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "service_account.json"
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# 📄 시트 정보 (코드에 직접 포함)
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
SHEET_NAME = "예측결과"
sheet = client.open_by_key(SPREADSHEET_ID)
worksheet = sheet.worksheet(SHEET_NAME)

# 🔢 현재 회차 구하기
existing = worksheet.get_all_records()
last_round = existing[-1]["회차"] if existing else 0
new_round = int(last_round) + 1

# 🔮 예측 결과 (현재는 예시 값)
predictions = ["RIGHT4EVEN", "LEFT3EVEN", "LEFT4ODD"]
prediction_str = " / ".join(predictions)

# 📅 날짜 포함하여 한 줄로 저장
now = datetime.now().strftime("%Y-%m-%d")
row = [now, new_round, "", "", "", prediction_str]
worksheet.append_row(row)
