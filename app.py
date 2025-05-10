from flask import Flask, jsonify
from predict import run_prediction

app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def predict_route():
    predictions = run_prediction()
    return jsonify({
        "예측 회차": predictions["round"],
        "1위": predictions["top3"][0],
        "2위": predictions["top3"][1],
        "3위": predictions["top3"][2],
        "1위(역방향)": predictions["top3_reverse"][0],
        "2위(역방향)": predictions["top3_reverse"][1],
        "3위(역방향)": predictions["top3_reverse"][2],
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
