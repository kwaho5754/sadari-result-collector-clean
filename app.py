import os
import json
import joblib
import gspread
import pandas as pd
from flask import Flask, jsonify
from datetime import datetime
from google.oauth2.service_account import Credentials
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split

app = Flask(__name__)

# ✅ 시트 공통 설정
SPREADSHEET_ID = '1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE'
SHEET_NAME = '예측결과'

def get_worksheet():
    SERVICE_ACCOUNT_JSON = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_JSON, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    worksheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    return worksheet

# ✅ [1] 예측
@app.route("/predict", methods=["GET"])
def predict():
    try:
        worksheet = get_worksheet()
        data = worksheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0]).tail(1000)

        last_round = int(df["회차"].iloc[-1])
        next_round = last_round + 1

        latest = df[["좌우", "줄수", "홀짝"]].tail(1)
        input_data = pd.get_dummies(latest)

        model = joblib.load("model.pkl")
        missing_cols = set(model.feature_names_in_) - set(input_data.columns)
        for col in missing_cols:
            input_data[col] = 0
        input_data = input_data[model.feature_names_in_]

        proba = model.predict_proba(input_data)[0]
        labels = model.classes_
        pred_dict = dict(zip(labels, proba))
        top_3 = sorted(pred_dict.items(), key=lambda x: x[1], reverse=True)[:3]
        predictions = [item[0] for item in top_3]

        # ✅ 예측 시간 및 모델 버전
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        model_time = datetime.fromtimestamp(os.path.getmtime("model.pkl")).strftime('%Y-%m-%d %H:%M:%S')

        result = {
            "round": next_round,
            "timestamp": now,
            "model_version": model_time,
            "results": predictions
        }

        with open("predict_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ [2] 실패 저장
@app.route("/save-failure", methods=["GET"])
def save_failure():
    try:
        worksheet = get_worksheet()
        data = worksheet.get_all_values()
        header, *rows = data
        last_row = rows[-1]
        actual = ''.join([last_row[2], last_row[3], last_row[4]]).upper()

        with open('predict_result.json', 'r', encoding='utf-8') as f:
            predict_data = json.load(f)
        predicted_list = predict_data['results']
        predict_round = predict_data['round']

        if actual not in predicted_list:
            try:
                with open('failures.json', 'r', encoding='utf-8') as f:
                    failures = json.load(f)
            except FileNotFoundError:
                failures = []

            failures.append({
                "timestamp": str(datetime.now()),
                "round": predict_round,
                "actual": actual,
                "predicted": predicted_list
            })

            # 중복 제거
            failures = [dict(t) for t in {tuple(d.items()) for d in failures}]
            with open('failures.json', 'w', encoding='utf-8') as f:
                json.dump(failures, f, indent=2, ensure_ascii=False)

            return jsonify({"message": f"❌ 오답 저장됨: {actual}"})
        else:
            return jsonify({"message": f"✅ 정답 포함됨: {actual}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ [3] 모델 재학습
@app.route("/train", methods=["GET"])
def train_model():
    try:
        worksheet = get_worksheet()
        data = worksheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0]).tail(1000)
        df['조합'] = df['좌우'].str.upper() + df['줄수'] + df['홀짝'].str.upper()

        X = pd.get_dummies(df[['좌우', '줄수', '홀짝']])
        y = df['조합']

        # 실패 데이터 불러오기
        try:
            with open('failures.json', 'r', encoding='utf-8') as f:
                failures = json.load(f)
        except FileNotFoundError:
            failures = []

        fail_df = pd.DataFrame([
            {
                '좌우': f['actual'][:5].replace('RIGHT', 'RIGHT').replace('LEFT', 'LEFT'),
                '줄수': f['actual'][5],
                '홀짝': f['actual'][6:],
                '조합': f['actual']
            }
            for f in failures
        ])
        fail_df = pd.concat([fail_df] * 3, ignore_index=True)

        # 통합 학습 데이터
        full_df = pd.concat([df[['좌우', '줄수', '홀짝', '조합']], fail_df], ignore_index=True)
        X_full = pd.get_dummies(full_df[['좌우', '줄수', '홀짝']])
        y_full = full_df['조합']

        X_train, X_test, y_train, y_test = train_test_split(X_full, y_full, test_size=0.2, random_state=42)
        model = GradientBoostingClassifier()
        model.fit(X_train, y_train)

        joblib.dump(model, "model.pkl")

        return jsonify({"message": "✅ 모델 재학습 완료 및 저장됨."})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
