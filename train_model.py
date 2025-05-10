import json
import os
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
import joblib

# ✅ 인증
SERVICE_ACCOUNT_JSON = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
creds = Credentials.from_service_account_info(
    SERVICE_ACCOUNT_JSON,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
client = gspread.authorize(creds)

# ✅ 시트 정보
SPREADSHEET_ID = '1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE'
SHEET_NAME = '예측결과'
worksheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# ✅ 시트 데이터 불러오기 (최근 1000줄)
data = worksheet.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])
df = df.tail(1000)  # 최근 1000줄 기준

# ✅ 전처리
df['조합'] = df['좌우'].str.upper() + df['줄수'] + df['홀짝'].str.upper()
X = pd.get_dummies(df[['좌우', '줄수', '홀짝']])
y = df['조합']

# ✅ 실패 케이스 불러오기 (보정용)
try:
    with open('failures.json', 'r', encoding='utf-8') as f:
        failures = json.load(f)
except FileNotFoundError:
    failures = []

# 실패 데이터 추가 (가중치 3배)
fail_df = pd.DataFrame([
    {
        '좌우': f['actual'][:5].replace('RIGHT', 'RIGHT').replace('LEFT', 'LEFT'),
        '줄수': f['actual'][5],
        '홀짝': f['actual'][6:],
        '조합': f['actual']
    }
    for f in failures
])
fail_df = pd.concat([fail_df] * 3, ignore_index=True)  # 3배 가중치

# ✅ 통합
full_df = pd.concat([df[['좌우', '줄수', '홀짝', '조합']], fail_df], ignore_index=True)
X_full = pd.get_dummies(full_df[['좌우', '줄수', '홀짝']])
y_full = full_df['조합']

# ✅ 학습
X_train, X_test, y_train, y_test = train_test_split(X_full, y_full, test_size=0.2, random_state=42)
model = GradientBoostingClassifier()
model.fit(X_train, y_train)

# ✅ 모델 저장
joblib.dump(model, 'model.pkl')
print("✅ 모델 재학습 완료 및 저장됨.")
