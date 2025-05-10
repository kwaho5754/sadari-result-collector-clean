import pandas as pd
import json
from datetime import datetime
import os
import gspread
import base64
from google.oauth2.service_account import Credentials

# 인증 함수
def get_gspread_client():
    b64_key = os.environ.get("SERVICE_ACCOUNT_BASE64")
    if not b64_key:
        raise Exception("환경변수 'SERVICE_ACCOUNT_BASE64'가 없습니다.")
    key_json = base64.b64decode(b64_key).decode("utf-8")
    creds_dict = json.loads(key_json)
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(credentials)

# 시트에서 실제 정답 불러오기
def load_latest_actual():
    gc = get_gspread_client()
    sheet = gc.open_by_key("1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE").worksheet("예측결과")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    def make_combo(row):
        lr = '좌' if row['좌우'] == 'LEFT' else '우'
        line = '삼' if row['줄수'] == 3 else '사'
        odd = '홀' if row['홀짝'] == 'ODD' else '짝'
        return f"{lr}{line}{odd}"

    df['조합'] = df.apply(make_combo, axis=1)
    return df.iloc[-1]['조합']

# 가장 최근 예측 결과 불러오기
def get_recent_prediction():
    try:
        with open('latest_prediction.json', 'r') as f:
            return json.load(f)
    except:
        return {}

# 오답 기록
def save_failure_case(predicted, actual, output_file='save_failure_case.json'):
    if actual in predicted:
        return

    record = {
        "timestamp": str(datetime.now()),
        "predicted": predicted,
        "actual": actual
    }

    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            data = json.load(f)
    else:
        data = []

    data.append(record)
    with open(output_file, 'w') as f:
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
