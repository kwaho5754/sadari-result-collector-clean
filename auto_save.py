import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

def save_latest_result():
    try:
        print("🚀 auto_save.py 시작")
        print("⏳ 환경변수 로딩 중...")
        SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")
        if not SERVICE_ACCOUNT_JSON:
            raise Exception("환경변수 'SERVICE_ACCOUNT_JSON'이 없습니다.")

        # 구글 시트 인증
        service_account_info = json.loads(SERVICE_ACCOUNT_JSON)
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
        gc = gspread.authorize(credentials)
        print("✅ 인증 완료")

        # 시트 열기
        SPREADSHEET_ID = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
        SHEET_NAME = "예측결과"
        worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        print("📄 시트 연결 완료")

        # 최신 JSON 데이터 요청
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        response = requests.get(url)
        data = response.json()

        recent = data[0]
        date = recent['reg_date']
        round_number = recent['date_round']
        position = recent['start_point']
        ladder_count = recent['line_count']
        oddeven = recent['odd_even']
        print(f"📋 최근 회차: {date}, {round_number}, {position}, {ladder_count}, {oddeven}")

        # 시트 데이터 확인 및 중복 검사
        try:
            existing_data = worksheet.get_all_records()
        except Exception as e:
            headers = worksheet.row_values(1)
            raise Exception(f"시트 1행(header)에 오류가 있습니다: {headers} → {str(e)}")

        is_duplicate = any(
            str(row.get('날짜')) == str(date) and str(row.get('회차')) == str(round_number)
            for row in existing_data
        )

        if is_duplicate:
            print(f"⚠️ 이미 저장된 회차: {date} - {round_number}")
        else:
            new_row = [date, round_number, position, ladder_count, oddeven]
            worksheet.append_row(new_row)
            print(f"✅ 저장 완료: {new_row}")

        print("🟢 저장 시도 완료 (코드 끝까지 정상 실행됨)")

    except Exception as e:
        print("❌ 예외 발생:", str(e))

if __name__ == "__main__":
    save_latest_result()