from flask import Flask, render_template_string
import pandas as pd
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# 구글 시트 인증 및 연결
SHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
SHEET_NAME = "예측결과"

def load_sheet_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = json.load(open("service_account.json"))
    client = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(creds, scope))
    sheet = client.open_by_key(SHEET_ID)
    worksheet = sheet.worksheet(SHEET_NAME)
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

def get_latest_prediction(df):
    try:
        latest_row = df.iloc[-1]
        date = latest_row["날짜"]
        episode = latest_row["회차"]
        left_right = latest_row["좌우"]
        count = latest_row["줄수"]
        odd_even = latest_row["홀짝"]
        prediction = f"{left_right}{count}{odd_even}"
        # 예측은 1~3위까지 설정한 구조 반영 (빈 칸일 수 있음)
        predictions = [prediction]
        for i in range(5, 8):
            if latest_row[i].strip():
                predictions.append(latest_row[i].strip())
        return date, episode, predictions
    except Exception as e:
        return "", "", ["오류 발생"]

@app.route("/predict")
def predict_view():
    df = load_sheet_data()
    date, episode, predictions = get_latest_prediction(df)

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>파워사다리 예측 결과</title>
    </head>
    <body>
        <h1>파워사다리 예측 결과</h1>
        <h3>예측 회차: {{ episode }}회차</h3>
        <ol>
            {% for p in predictions %}
                <li>{{ p }}</li>
            {% endfor %}
        </ol>
    </body>
    </html>
    """
    return render_template_string(html_template, episode=episode, predictions=predictions)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
