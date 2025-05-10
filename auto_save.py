import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

def save_latest_result():
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
    position = recent['position']
    ladder_count = recent['ladderCount']
    oddeven = recent['oddEven']

    # --- 4. 시트에 이미 있는지 확인 ---
    existing_data = worksheet.get_all_records()
    is_duplicate = any(
        str(row.get('date')) == str(date) and str(row.get('round')) == str(round_number)
        for row in existing_data
    )

    if is_duplicate:
        print(f"✅ 이미 저장된 회차입니다: {date} - {round_number}회차")
    else:
        new_row = [date, round_number, position, ladder_count, oddeven]
        worksheet.append_row(new_row)
        print(f"✅ 저장 완료: {new_row}")

# --- 5. 실행 엔트리포인트 추가 ---
if __name__ == "__main__":
    print("⏳ auto_save.py 실행 시작...")
    save_latest_result()
