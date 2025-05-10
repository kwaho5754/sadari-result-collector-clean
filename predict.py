import gspread
from oauth2client.service_account import ServiceAccountCredentials
from collections import Counter

def run_prediction():
    # Google Sheets 연동
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1j72Y36aXDYTxsJId92DCnQLouwRgHL2BBOqI9UUDQzE/edit#gid=0").worksheet("예측결과")
    data = sheet.get_all_values()[1:]  # 헤더 제외

    if len(data) < 10:
        return {
            "round": "데이터 부족",
            "top3": [],
        }

    def extract_combinations(rows):
        return [f"{row[2]}{row[3]}{row[4]}" for row in rows if len(row) >= 5]

    # 정방향 + 역방향 조합 추출
    forward_combos = extract_combinations(data[-1000:])
    backward_combos = extract_combinations(data[-1000:][::-1])

    combined = forward_combos + backward_combos
    counter = Counter(combined)
    sorted_combos = sorted(counter.items(), key=lambda x: (-x[1], x[0]))

    # 중복 제거한 상위 3개 추출
    unique_combos = []
    for combo, _ in sorted_combos:
        if combo not in unique_combos:
            unique_combos.append(combo)
        if len(unique_combos) == 3:
            break

    # 다음 회차 추정
    last = data[-1]
    next_round = int(last[1]) + 1
    next_date = last[0]

    result = [next_date, str(next_round)]
    for combo in unique_combos:
        side = "LEFT" if "LEFT" in combo or combo.startswith("L") else "RIGHT"
        line = "3" if "3" in combo else "4"
        parity = "EVEN" if "EVEN" in combo or "짝" in combo else "ODD"
        result.extend([side, line, parity])

    return {
        "round": result[1],
        "top3": result[2:]
    }
