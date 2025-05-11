from flask import Flask, jsonify, request
import pandas as pd
import joblib
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# 🔐 구글 시트 인증
SERVICE_ACCOUNT_FILE = 'service_account.json'
SPREADSHEET_ID = '1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4'
SHEET_NAME = '예측결과'

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# ✅ 모델과 인코더 불러오기
model = joblib.load('stacking_model.pkl')
le_target = joblib.load('label_encoder.pkl')

# ✅ 예측 함수
def predict_latest():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
        return "시트에 데이터가 없습니다."

    latest = df.tail(1).copy()
    latest_result = latest['결과'].values[0]

    # 특성 분해
    def parse_combination(x):
        lr = '좌' if '좌' in x else '우'
        ladder = '3' if '삼' in x else '4'
        oddeven = '홀' if '홀' in x else '짝'
        return pd.Series([lr, ladder, oddeven])

    latest[['LR', 'LADDER', 'ODDEVEN']] = latest['결과'].apply(parse_combination)
    X = pd.get_dummies(latest[['LR', 'LADDER', 'ODDEVEN']])
    
    # 누락된 더미 컬럼 채우기
    model_cols = model.get_booster().feature_names
    for col in model_cols:
        if col not in X.columns:
            X[col] = 0
    X = X[model_cols]

    pred = model.predict(X)
    result = le_target.inverse_transform(pred)

    return result[0]

# ✅ API 엔드포인트
@app.route('/predict', methods=['GET'])
def predict():
    try:
        result = predict_latest()
        return jsonify({"예측결과": result})
    except Exception as e:
        return jsonify({"오류": str(e)})

# ✅ 서버 실행 (Railway용)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
