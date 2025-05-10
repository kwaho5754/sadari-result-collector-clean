from flask import Flask, jsonify
import json
import os
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# ✅ 환경변수에서 서비스 계정 JSON 불러오기
service_account_json = os.environ["SERVICE_ACCOUNT_JSON"]
service_account_info = json.loads(service_account_json)
service_account_info["private_key"] = service_account_info["private_key"].replace("\\n", "\n")

# ✅ 인증
credentials = Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(credentials)

# ✅ 시트 연결 (시트 ID 정확히 반영)
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"

try:
    worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet("예측결과")
except Exception as e:
    worksheet = None
    print(f"🔴 시트 연결 실패: {e}")

# ✅ API 라우터
@app.route("/predict")
def predict():
    if worksheet is None:
        return jsonify({"error": "Google Sheet 연결 실패"}), 500
    try:
        values = worksheet.get_all_values()
        latest_row = values[-1] if values else []
        return jsonify({"latest_prediction": latest_row})
    except Exception as e:
        return jsonify({"error": f"시트 데이터 조회 실패: {str(e)}"}), 500

# ✅ 서버 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
