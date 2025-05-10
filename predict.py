import pandas as pd
import json
import gspread
from collections import Counter
from google.oauth2.service_account import Credentials

def get_sheet_data():
    creds = Credentials.from_service_account_file("service_account.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE")
    worksheet = sheet.worksheet("예측결과")
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    return df.tail(1000)  # 최근 1000줄

def extract_combinations(df):
    return (df['좌우'].str.upper() + df['줄수'] + df['홀짝'].str.upper()).tolist()

def analyze_direction(combinations, reverse=False):
    if reverse:
        combinations = combinations[::-1]
    block_lengths = [3, 4, 5]
    scores = Counter()

    for block_len in block_lengths:
        for i in range(len(combinations) - block_len):
            current_block = combinations[i:i+block_len]
            for combo in set(current_block):
                scores[combo] += 1

    # 상위/하위/중간 추출
    sorted_items = sorted(scores.items(), key=lambda x: x[1])
    top3 = []
    seen = set()
    for item in [sorted_items[0], sorted_items[-1], sorted_items[len(sorted_items)//2]]:
        if item[0] not in seen:
            top3.append(item[0])
            seen.add(item[0])
        if len(top3) == 3:
            break
    return top3

def run_prediction():
    df = get_sheet_data()
    combinations = extract_combinations(df)

    top3_forward = analyze_direction(combinations, reverse=False)
    top3_reverse = analyze_direction(combinations, reverse=True)

    try:
        last_round = int(df.iloc[-1]['회차']) + 1
    except:
        last_round = "Unknown"

    result = {
        "round": last_round,
        "top3": top3_forward,
        "top3_reverse": top3_reverse
    }

    # 예측 결과 저장
    with open("predict_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result
