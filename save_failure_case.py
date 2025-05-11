import json
import os
from datetime import datetime
from helper import get_latest_actual_combo  # 시트에서 실제값 가져오기

# 파일 경로
PREDICTION_FILE = "latest_prediction.json"
FAILURE_LOG_FILE = "save_failure_case.json"

def load_latest_prediction():
    if not os.path.exists(PREDICTION_FILE):
        raise FileNotFoundError(f"{PREDICTION_FILE} 파일이 없습니다.")

    with open(PREDICTION_FILE, "r", encoding='utf-8') as f:
        data = json.load(f)
    return data["예측회차"], data["예측결과"]

def save_failure(predicted, actual, round_info):
    log = []
    if os.path.exists(FAILURE_LOG_FILE):
        with open(FAILURE_LOG_FILE, "r", encoding='utf-8') as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []

    log.append({
        "날짜시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "예측회차": round_info,
        "예측값": predicted,
        "정답": actual
    })

    with open(FAILURE_LOG_FILE, "w", encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def run_failure_check():
    try:
        round_info, predicted_list = load_latest_prediction()
        actual = get_latest_actual_combo()

        if actual not in predicted_list:
            print(f"❌ 예측 실패: 실제값 {actual} 은 예측값 {predicted_list}에 없음")
            save_failure(predicted_list, actual, round_info)
        else:
            print(f"✅ 예측 성공: {actual} 이 예측값에 포함됨")

    except Exception as e:
        print("❗ 오류 발생:", e)

# 직접 실행 시
if __name__ == "__main__":
    run_failure_check()
