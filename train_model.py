import pandas as pd
import numpy as np
import json
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 설정
SPREADSHEET_ID = '1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE'
SHEET_NAME = '예측결과'
JSON_KEY_FILE = 'service_account.json'
FAILURE_JSON = 'save_failure_case.json'

# 조합 인코더
combos = ['좌삼짝', '우삼홀', '좌사홀', '우사짝']
encoder = LabelEncoder()
encoder.fit(combos)

# 시트 불러오기
def load_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scope)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    df['조합'] = df.apply(lambda row: '좌' if row['좌우'] == 'LEFT' else '우', axis=1)
    df['조합'] += df['줄수'].map({3: '삼', 4: '사'})
    df['조합'] += df['홀짝'].map({'ODD': '홀', 'EVEN': '짝'})
    return df.tail(1000)

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
def add_failure_data(X, y):
    try:
        with open(FAILURE_JSON, 'r') as f:
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
