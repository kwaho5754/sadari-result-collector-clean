import os
import json
import gspread
from google.oauth2.service_account import Credentials

# 환경변수에서 서비스 계정 JSON 문자열 불러오기
service_account_json = os.environ["SERVICE_ACCOUNT_JSON"]
service_account_info = json.loads(service_account_json)

# private_key 줄바꿈 복원
service_account_info["private_key"] = service_account_info["private_key"].replace("\\n", "\n")

# 인증 및 구글 시트 접근
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(service_account_info, scopes=scope)
gc = gspread.authorize(credentials)

# 주어진 Google Sheets 문서 ID와 시트 이름
sheet = gc.open_by_key("1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE")
worksheet = sheet.worksheet("예측결과")

# 테스트 출력
print("✅ 시트 열기 성공:", worksheet.title)
