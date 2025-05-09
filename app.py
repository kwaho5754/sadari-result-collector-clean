from flask import Flask, jsonify
import json
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# 환경변수 또는 파일에서 서비스 계정 불러오기
with open("service_account.json", "r", encoding="utf-8") as f:
    service_account_info = json.load(f)

credentials = Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

gc = gspread.authorize(credentials)

SPREADSHEET_ID = '1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4'
worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet("예측결과")

@app.route('/predict')
def predict():
    values = worksheet.get_all_values()
    latest_row = values[-1] if values else []
    return jsonify({"latest_prediction": latest_row})

if __name__ == '__main__':
    app.run()
