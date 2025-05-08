from flask import Flask, jsonify
import gspread
import json
import requests
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

# 환경변수에서 JSON 키를 읽어와 인증
import os
service_account_info = json.loads(os.environ['SERVICE_ACCOUNT_JSON_RAW'])
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
gc = gspread.authorize(credentials)

# Google Sheet 정보
SPREADSHEET_ID = '1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4'  # 시트 ID
worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet('예측결과')   # 시트 이름

@app.route('/run-save')
def run_save():
    try:
        # 실시간 JSON 데이터 불러오기
        url = 'https://ntry.com/data/json/games/power_ladder/recent_result.json'
        res = requests.get(url)
        data = res.json()

        reg_date = data['date']
        round_num = int(data['round'])
        position = data['position']
        ladder = int(data['ladder'])
        oddeven = data['oddeven']

        # 시트에서 마지막 회차 가져오기
        records = worksheet.get_all_records()
        existing_rounds = [int(row['회차']) for row in records if str(row.get('날짜')) == reg_date]

        # 이미 저장된 회차인지 확인
        if round_num in existing_rounds:
            return jsonify({'status': 'skipped', 'message': f'{round_num}회차 이미 저장됨'})

        # 저장할 데이터 행
        row = [reg_date, round_num, position, ladder, oddeven]
        worksheet.append_row(row)

        return jsonify({'status': 'saved', 'message': f'{round_num}회차 저장 완료'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/')
def home():
    return '✅ 사다리 자동저장 서버 작동 중입니다.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
