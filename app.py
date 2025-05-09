from flask import Flask, jsonify
import json
import os
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# ✅ 환경변수에서 JSON 문자열 불러오기
service_account_json = os.environ["SERVICE_ACCOUNT_JSON"]
service_account_info = json.loads(service_account_json)
service_account_info["private_key"] = service_account_info["private_key"].replace("\\n", "\n")

# ✅ 인증 처리
credentials = Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(credentials)

# ✅ 시트 연결
SPREADSHEET_ID = '1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4'
worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet("예측결과")

@app.route('/predict')
def predict():
    values = worksheet.get_all_values()
    latest_row = values[-1] if values else []
    return jsonify({"latest_prediction": latest_row})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)


