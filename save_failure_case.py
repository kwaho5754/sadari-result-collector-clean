import pandas as pd
import json
from datetime import datetime
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 설정
SPREADSHEET_ID = '1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE'
SHEET_NAME = '예측결과'
JSON_KEY_FILE = 'service_account.json'
FAILURE_JSON = 'save_failure_case.json'

# 대조 대상 예측값 (실제로는 app.py에서 전달 or 파일로 받아옴)
def get_recent_prediction():
    try:
        with open('latest_prediction.json', 'r') as f:
            return json.load(f)
    except:
        return {}

# 실시간 시트에서 최근 정답 조합 가져오기
def load_latest_actual():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scope)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    # 조합 생성
    def make_combo(row):
        lr = '좌' if row['좌우'] == 'LEFT' else '우'
        line = '삼' if row['줄수'] == 3 else '사'
        odd = '홀' if row['홀짝'] == 'ODD' else '짝'
        return f"{lr}{line}{odd}"

    df['조합'] = df.apply(make_combo, axis=1)
    return df.iloc[-1]['조합']

# 오답 저장
def save_failure_case(predicted, actual):
    if actual in predicted:
        return  # 정답 있음 → 오답 아님

    record = {
        "timestamp": str(datetime.now()),
        "predicted": predicted,
        "actual": actual
    }

    if os.path.exists(FAILURE_JSON):
        with open(FAILURE_JSON, 'r') as f:
            data = json.load(f)
    else:
        data = []

    data.append(record)

    with open(FAILURE_JSON, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    prediction = get_recent_prediction()
    if prediction:
        predicted_list = [
            prediction.get('1위'),
            prediction.get('2위'),
            prediction.get('3위')
        ]
        actual_combo = load_latest_actual()
        save_failure_case(predicted_list, actual_combo)
