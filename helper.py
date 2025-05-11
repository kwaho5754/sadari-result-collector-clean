import os
import json
import base64
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# ✅ 환경변수에서 Base64로 저장된 서비스 계정 키 불러오기
def get_gspread_client():
    b64_key = os.environ.get("SERVICE_ACCOUNT_BASE64")
    if not b64_key:
        raise Exception("환경변수 'SERVICE_ACCOUNT_BASE64'가 설정되지 않았습니다.")

    key_json = base64.b64decode(b64_key).decode("utf-8")
    creds_dict = json.loads(key_json)

    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(credentials)

# ✅ 시트에서 가장 마지막 회차의 실제 결과 조합 불러오기
def get_latest_actual_combo():
    gc = get_gspread_client()
    sheet = gc.open_by_key("1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE").worksheet("예측결과")
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    def make_combo(row):
        lr = '좌' if row['좌우'] == 'LEFT' else '우'
        line = '삼' if row['줄수'] == 3 else '사'
        odd = '홀' if row['홀짝'] == 'ODD' else '짝'
        return f"{lr}{line}{odd}"

    df['조합'] = df.apply(make_combo, axis=1)
    return df.iloc[-1]['조합']

# ✅ 가장 최근 회차 번호 가져오기 (선택용)
def get_latest_round_number():
    gc = get_gspread_client()
    sheet = gc.open_by_key("1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE").worksheet("예측결과")
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    return df.iloc[-1]['회차']
