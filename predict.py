import os
import json
import joblib
import gspread
import pandas as pd
from flask import Flask, jsonify
from google.oauth2.service_account import Credentials

app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def predict():
    try:
        # ✅ 인증
        SERVICE_ACCOUNT_JSON = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
        creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_JSON, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        client = gspread.authorize(creds)

        # ✅ 시트 설정
        SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
        SHEET_NAME = "예측결과"
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        data = sheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])
        df = df.tail(1000)  # 최근 1000줄 기준

        # ✅ 마지막 회차 추정
        last_round = int(df["회차"].iloc[-1])
        next_round = last_round + 1

        # ✅ 입력 데이터 처리
        latest = df[["좌우", "줄수", "홀짝"]].tail(1)
        input_data = pd.get_dummies(latest)

        # ✅ 모든 가능한 조합에 대해 예측 확률 계산
        model = joblib.load("model.pkl")
        all_combinations = pd.get_dummies(df[["좌우", "줄수", "홀짝"]])
        missing_cols = set(model.feature_names_in_) - set(input_data.columns)
        for col in missing_cols:
            input_data[col] = 0
        input_data = input_data[model.feature_names_in_]

        proba = model.predict_proba(input_data)[0]
        labels = model.classes_
        pred_dict = dict(zip(labels, proba))

        # ✅ 상위 3개 예측 결과 추출
        top_3 = sorted(pred_dict.items(), key=lambda x: x[1], reverse=True)[:3]
        predictions = [item[0] for item in top_3]

        # ✅ 응답 구조
        result = {
            "round": next_round,
            "results": predictions
        }

        # ✅ 예측 결과 저장 (오답 체크용)
        with open("predict_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
