import pandas as pd
import json
import gspread
from collections import Counter
from google.oauth2.service_account import Credentials

# ✅ 시트 인증
SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
SHEET_NAME = "예측결과"

def get_sheet_data():
    creds = Credentials.from_service_account_file("service_account.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    data = sheet.get_all_values()
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
    if len(sorted_items) >= 3:
        top3 = [sorted_items[0][0], sorted_items[-1][0], sorted_items[len(sorted_items)//2][0]]
    elif len(sorted_items) > 0:
        top3 = [x[0] for x in sorted_items[:3]]
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

    return {
        "round": last_round,
        "top3": top3_forward,
        "top3_reverse": top3_reverse
    }
