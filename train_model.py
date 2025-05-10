import pandas as pd
import numpy as np
import json
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
import gspread
import os
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

# 시트 불러오기
def load_sheet():
    gc = get_gspread_client()
    sheet = gc.open_by_key("1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE").worksheet("예측결과")
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    df['조합'] = df.apply(lambda row: '좌' if row['좌우'] == 'LEFT' else '우', axis=1)
    df['조합'] += df['줄수'].map({3: '삼', 4: '사'})
    df['조합'] += df['홀짝'].map({'ODD': '홀', 'EVEN': '짝'})
    return df.tail(1000)

# 조합 인코더
combos = ['좌삼짝', '우삼홀', '좌사홀', '우사짝']
encoder = LabelEncoder()
encoder.fit(combos)

# 유동 블럭 학습 데이터 구성
def create_training_data(df, block_sizes=[3,4,5]):
    X, y = [], []
    combo_seq = df['조합'].tolist()
    for size in block_sizes:
        for i in range(len(combo_seq) - size):
            block = combo_seq[i:i+size]
            target = combo_seq[i+size]
            X.append(encoder.transform(block))
            y.append(encoder.transform([target])[0])
    return np.array(X), np.array(y)

# 오답 추가
def add_failure_data(X, y, failure_file='save_failure_case.json'):
    try:
        with open(failure_file, 'r') as f:
            data = json.load(f)
        for case in data:
            pred = case['predicted']
            actual = case['actual']
            block = encoder.transform(pred)
            X = np.vstack([X, block])
            y = np.append(y, encoder.transform([actual])[0])
    except:
        pass
    return X, y

if __name__ == "__main__":
    df = load_sheet()
    X, y = create_training_data(df)
    X, y = add_failure_data(X, y)

    model = GradientBoostingClassifier()
    model.fit(X, y)
    joblib.dump(model, 'model.pkl')
    print("✅ 모델 재학습 완료 및 저장됨.")
