from flask import Flask, jsonify
from predict import run_prediction

app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def predict_route():
    predictions = run_prediction()
    return jsonify({
        "예측 회차": predictions["round"],
        "1위": predictions["top3"][0] if len(predictions["top3"]) > 0 else "",
        "2위": predictions["top3"][1] if len(predictions["top3"]) > 1 else "",
        "3위": predictions["top3"][2] if len(predictions["top3"]) > 2 else ""
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
