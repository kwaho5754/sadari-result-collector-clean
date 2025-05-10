import gspread
import json
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier

# 인증
SERVICE_ACCOUNT_JSON = os.environ['SERVICE_ACCOUNT_JSON']
creds = json.loads(SERVICE_ACCOUNT_JSON)
client = gspread.service_account_from_dict(creds)

# 시트 정보
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
SHEET_NAME = "예측결과"
sheet = client.open_by_key(SPREADSHEET_ID)
worksheet = sheet.worksheet(SHEET_NAME)

# 데이터 불러오기
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# 예측값이 없는 행 제외
df = df[df['예측값'].notnull()]
if df.empty:
    print("학습할 데이터가 없습니다.")
    exit()

# 입력(X), 타겟(Y) 분리
X = df[['좌우', '줄수', '홀짝']]
y = df['예측값']

# 학습 예시 (변환 생략 가능)
X_encoded = pd.get_dummies(X)
model = GradientBoostingClassifier()
model.fit(X_encoded, y)

print("✅ 자동 학습 완료")
