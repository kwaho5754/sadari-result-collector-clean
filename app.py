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
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet("예측결과")

@app.route('/predict')
def predict():
    try:
        values = worksheet.get_all_values()
        latest_row = values[-1] if values else []
        
        if len(latest_row) >= 8:
            result = {
                "latest_prediction": latest_row
            }
        else:
            result = {
                "error": "예측 결과 항목이 부족합니다.",
                "latest_row": latest_row
            }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
