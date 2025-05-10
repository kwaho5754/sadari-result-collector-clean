from flask import Flask, jsonify
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
import json
import random
import os

app = Flask(__name__)

# 대칭 규칙 정의
def mirror(combo):
    table = {
        '좌삼짝': '우삼홀', '우삼홀': '좌삼짝',
        '좌사홀': '우사짝', '우사짝': '좌사홀'
    }
    return table.get(combo, combo)

# 좌우 + 줄수 + 홀짝 → 조합 이름 만들기
def make_combo(row):
    lr = '좌' if row['좌우'] == 'LEFT' else '우'
    line = '삼' if row['줄수'] == 3 else '사'
    odd = '홀' if row['홀짝'] == 'ODD' else '짝'
    return f"{lr}{line}{odd}"

# Google Sheets에서 데이터 불러오기
def load_sheet_data():
    json_key = os.environ.get("SERVICE_ACCOUNT_JSON")
    if not json_key:
        raise Exception("환경변수 'SERVICE_ACCOUNT_JSON'이 없습니다.")

    creds_dict = json.loads(json_key)
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(credentials)

    SPREADSHEET_ID = "1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE"
    SHEET_NAME = "예측결과"
    sheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df['조합'] = df.apply(make_combo, axis=1)
    return df

# 3~5줄 블럭 유동 분석 (정방향 또는 역방향)
def extract_blocks(combo_list, reverse=False):
    blocks = []
    combo_list = combo_list[::-1] if reverse else combo_list
    for size in [3, 4, 5]:
        for i in range(len(combo_list) - size + 1):
            block = tuple(combo_list[i:i+size])
            blocks.append(block)
    return blocks

# 예측값 선정 로직 (가장 적은/많은/중간)
def select_final_predictions(combo_list):
    counts = pd.Series(combo_list).value_counts()
    if len(counts) < 3:
        all_items = counts.index.tolist()
        while len(all_items) < 3:
            all_items.append(random.choice(['좌삼짝', '우삼홀', '좌사홀', '우사짝']))
        return list(set(all_items))[:3]
    sorted_items = counts.sort_values()
    return [sorted_items.index[0], sorted_items.index[-1], sorted_items.index[len(sorted_items)//2]]

# 예측 회차 계산
def get_next_round(df):
    last_date = df.iloc[-1]['날짜']
    last_round = int(df.iloc[-1]['회차'])
    next_round = last_round + 1 if last_round < 288 else 1
    next_date = last_date if next_round != 1 else str((pd.to_datetime(last_date) + timedelta(days=1)).date())
    return f"{next_date} / {next_round}회차"

@app.route('/predict', methods=['GET'])
def predict():
    try:
        df = load_sheet_data()
        df = df.tail(1000)

        combo_seq = df['조합'].tolist()

        # 정방향 & 역방향 분석
        forward_blocks = extract_blocks(combo_seq, reverse=False)
        backward_blocks = extract_blocks(combo_seq, reverse=True)

        forward_end = [block[-1] for block in forward_blocks]
        backward_end = [block[-1] for block in backward_blocks]

        candidates = forward_end + backward_end

        top3 = select_final_predictions(candidates)
        final_result = [mirror(combo) for combo in top3]

        next_round_str = get_next_round(df)

        result = {
            '예측 회차': next_round_str,
            '예측 결과': [
                f"1위: {final_result[0]}",
                f"2위: {final_result[1]}",
                f"3위: {final_result[2]}"
            ]
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({'오류': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render용
    app.run(host='0.0.0.0', port=port)
