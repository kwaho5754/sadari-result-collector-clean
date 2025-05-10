from flask import Flask, jsonify
from predict import run_prediction

app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def predict_route():
    predictions = run_prediction()
    return jsonify({
        "예측 회차": predictions["round"],
        "예측값1": predictions["top3"][0],
        "예측값2": predictions["top3"][1],
        "예측값3": predictions["top3"][2]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
# force update
