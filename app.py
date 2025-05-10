from flask import Flask, jsonify, render_template_string
import pandas as pd
from train_model import train_model
from predict import predict_top_3

app = Flask(__name__)

SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
SHEET_NAME = "예측결과"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>파워사다리 예측 결과</title>
</head>
<body>
    <h1>파워사다리 예측 결과</h1>
    <h2>예측 회차: {{ round }}회차</h2>
    <ol>
        {% for p in predictions %}
        <li>{{ p }}</li>
        {% endfor %}
    </ol>
</body>
</html>
"""

@app.route("/predict")
def predict():
    # 전체 시트 불러오기
    df = pd.read_csv("https://docs.google.com/spreadsheets/d/" + SPREADSHEET_ID + "/export?format=csv&gid=0")

    # 최근 1000줄 기준 학습
    df_recent = df.iloc[-1000:] if len(df) >= 1000 else df
    
    # 학습
    model = train_model(df_recent)

    # 예측값 3개 생성
    predictions = predict_top_3(model, df_recent)

    # 다음 회차 예측
    last_round = int(df_recent.iloc[-1]["회차"])
    next_round = last_round + 1

    return render_template_string(HTML_TEMPLATE, round=next_round, predictions=predictions)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
