import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

def save_latest_result():
    try:
        print("🚀 auto_save.py 시작")
        SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")
        if not SERVICE_ACCOUNT_JSON:
            raise Exception("환경변수 'SERVICE_ACCOUNT_JSON'이 없습니다.")

        # 인증
        creds = json.loads(SERVICE_ACCOUNT_JSON)
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_info(creds, scopes=scopes)
        client = gspread.authorize(credentials)

        # 시트 연결
        SPREADSHEET_ID = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
        SHEET_NAME = "예측결과"
        sheet = client.open_by_key(SPREADSHEET_ID)
        worksheet = sheet.worksheet(SHEET_NAME)

        # JSON 데이터
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

        # 전체 값 가져오기 (안정적 방식)
        all_values = worksheet.get_all_values()
        headers = all_values[0]
        records = all_values[1:]

        # 열 인덱스 매핑
        try:
            idx_date = headers.index("날짜")
            idx_round = headers.index("회차")
        except ValueError:
            raise Exception(f"❌ 시트 헤더에 '날짜', '회차' 열이 없습니다. 현재 헤더: {headers}")

        # 중복 확인
        is_duplicate = any(
            row[idx_date] == str(date) and row[idx_round] == str(round_number)
            for row in records
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