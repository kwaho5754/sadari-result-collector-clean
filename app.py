import os
import json
from flask import Flask, jsonify
from predict import predict_final_3  # 예측 함수
from datetime import datetime

app = Flask(__name__)

@app.route('/predict', methods=['GET'])
def predict_route():
    try:
        predictions, round_info = predict_final_3()  # 3개 예측값 + 회차 정보 반환
        result = {
            "예측회차": round_info,
            "예측결과": predictions
        }

        # ✅ 예측 결과를 latest_prediction.json으로 저장
        with open("latest_prediction.json", "w", encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return jsonify(result)

    except Exception as e:
        return jsonify({"오류": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
