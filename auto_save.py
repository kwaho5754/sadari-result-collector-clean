import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

def save_latest_result():
    try:
        print("⏳ 시작: 환경변수 로딩 중...")
        SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")
        if not SERVICE_ACCOUNT_JSON:
            raise Exception("환경변수 'SERVICE_ACCOUNT_JSON'이 없습니다.")

        print("✅ 인증 시작")
        service_account_info = json.loads(SERVICE_ACCOUNT_JSON)
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
        gc = gspread.authorize(credentials)

        print("📄 시트 열기")
        SPREADSHEET_ID = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
        SHEET_NAME = "예측결과"
        worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

        print("🌐 JSON 데이터 요청 중...")
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        response = requests.get(url)
        data = response.json()

        print("🔍 최신 회차 데이터 추출")
        recent = data[0]
        date = recent['reg_date']
        round_number = recent['date_round']
        position = recent['start_point']
        ladder_count = recent['line_count']
        oddeven = recent['odd_even']

        print(f"📋 최근 회차: {date}, {round_number}, {position}, {ladder_count}, {oddeven}")

        print("📑 시트에서 중복 확인 중...")
        existing_data = worksheet.get_all_records()
        is_duplicate = any(
            str(row.get('date')) == str(date) and str(row.get('round')) == str(round_number)
            for row in existing_data
        )

        if is_duplicate:
            print(f"⚠️ 이미 저장됨: {date} - {round_number}회차")
        else:
            new_row = [date, round_number, position, ladder_count, oddeven]
            worksheet.append_row(new_row)
            print(f"✅ 저장 완료: {new_row}")

    except Exception as e:
        print("❌ 예외 발생:", str(e))

if __name__ == "__main__":
    print("🚀 auto_save.py 시작")
    save_latest_result()
