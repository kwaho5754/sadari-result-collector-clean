import pandas as pd
import joblib
from google.oauth2.service_account import Credentials
import gspread
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

# ✅ 구글 시트 연동 설정
SERVICE_ACCOUNT_FILE = 'service_account.json'
SPREADSHEET_ID = '1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4'
SHEET_NAME = '예측결과'

# ✅ 인증 및 시트 연결
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# ✅ 헤더를 명시적으로 지정 (중복 회피)
expected_headers = ["날짜", "회차", "좌우", "줄수", "홀짝"]
data = sheet.get_all_records(expected_headers=expected_headers)
df = pd.DataFrame(data)

# ✅ 최근 1000줄만 사용
df = df.tail(1000)

# ✅ 좌우/줄수/홀짝 → 조합 문자열로 결과 생성
def make_result(row):
    lr = '우' if row['좌우'] == 'RIGHT' else '좌'
    ladder = '삼' if int(row['줄수']) == 3 else '사'
    odd_even = '짝' if row['홀짝'] == 'EVEN' else '홀'
    return lr + ladder + odd_even

df['결과'] = df.apply(make_result, axis=1)

# ✅ 결과 → 예측 타겟으로 변환
le_target = LabelEncoder()
df['target'] = le_target.fit_transform(df['결과'])

# ✅ 특성 만들기
X = df[['좌우', '줄수', '홀짝']]
X_encoded = pd.get_dummies(X)
y = df['target']

# ✅ 모델 학습
model = XGBClassifier()
model.fit(X_encoded, y)

# ✅ 모델과 인코더 저장
joblib.dump(model, 'stacking_model.pkl')
joblib.dump(le_target, 'label_encoder.pkl')

print("✅ 모델 학습 완료 및 저장됨.")
