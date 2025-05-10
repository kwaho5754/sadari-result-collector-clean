# predict_train.py
import os
import json
import gspread
import numpy as np
from google.oauth2.service_account import Credentials
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

# === 1. 시트 불러오기 ===
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_JSON = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
SHEET_NAME = "예측결과"

creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_JSON, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
data = sheet.get_all_records()

# === 2. 최근 1000줄 데이터 구성 ===
df = data[-1000:] if len(data) >= 1000 else data

# === 3. X, y 구성 ===
X, y = [], []
def pattern(row):
    return f"{row['좌우']}-{row['줄수']}-{row['홀짝']}"

patterns = [pattern(row) for row in df]
for i in range(len(patterns) - 5):
    X.append(patterns[i:i+3])  # 최근 3줄
    y.append(patterns[i+3])    # 그다음 줄 예측 대상

# === 4. 전처리 ===
enc = LabelEncoder()
flat_X = [" ".join(x) for x in X]
X_enc = enc.fit_transform(flat_X).reshape(-1, 1)
y_enc = enc.fit_transform(y)

# === 5. 모델 학습 ===
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_enc, y_enc)

# === 6. 최신 흐름 기반 예측 ===
latest_input = " ".join(patterns[-3:])
x_pred_enc = enc.transform([latest_input]).reshape(-1, 1)
y_probs = model.predict_proba(x_pred_enc)[0]

# === 7. 상위 3개 예측 조합 추출 ===
top_indices = np.argsort(y_probs)[::-1][:3]
top_labels = enc.inverse_transform(top_indices)
prediction_result = "/".join(top_labels)

# === 8. 시트에 저장 ===
now = datetime.now().strftime("%Y-%m-%d")
latest_row = data[-1]
next_round = int(latest_row['회차']) + 1
row = [now, next_round, "-", "-", "-", prediction_result]  # 좌우, 줄수, 홀짝은 예측 X
sheet.append_row(row)

print(f"✅ 예측값 저장 완료: {now} {next_round}회차 → {prediction_result}")
