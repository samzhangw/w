from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import random
import string
import time

app = Flask(__name__)

# 成績對應積分
score_to_points = {
    'A': 6,
    'B': 4,
    'C': 2,
    '作文': {0: 0, 1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3}
}

# 成績對應積點
score_to_credit = {
    'A++': 7,
    'A+': 6,
    'A': 5,
    'B++': 4,
    'B+': 3,
    'B': 2,
    'C': 1
}

# 學校錄取標準
schools = {
    '武陵高中': {'points': 33, 'credits': 32, 'type': '普通科'},
    '中壢高中': {'points': 31, 'credits': 28, 'type': '普通科'},
    '內壢高中': {'points': 29, 'credits': 24, 'type': '普通科'},
    '陽明高中': {'points': 27, 'credits': 22, 'type': '普通科'},
    '平鎮高中': {'points': 27, 'credits': 21, 'type': '普通科'},
    '永豐高中': {'points': 25, 'credits': 20, 'type': '普通科'},
    '大園高中': {'points': 25, 'credits': 19, 'type': '普通科'},
    '南崁高中': {'points': 25, 'credits': 16, 'type': '普通科'},
    '壽山高中': {'points': 25, 'credits': 14, 'type': '普通科'},
    '龍潭高中': {'points': 23, 'credits': 17, 'type': '普通科'},
    '楊梅高中': {'points': 23, 'credits': 15, 'type': '普通科'},
    '觀音高中': {'points': 23, 'credits': 11, 'type': '普通科'},
    '大溪高中': {'points': 23, 'credits': 10, 'type': '普通科'},
    '中壢高商(綜合科)': {'points': 25, 'credits': 24, 'type': '職業類科'},
    '中壢高商(商業經營科)': {'points': 23, 'credits': 15, 'type': '職業類科'},
    '中壢高商(資料處理科)': {'points': 23, 'credits': 15, 'type': '職業類科'},
    '中壢高商(國際貿易科)': {'points': 23, 'credits': 14, 'type': '職業類科'},
    '壽山高中(國際貿易)': {'points': 23, 'credits': 15, 'type': '職業類科'},
    '壽山高中(應用英語科)': {'points': 23, 'credits': 15, 'type': '職業類科'},
    '壽山高中(廣告設計科)': {'points': 23, 'credits': 14, 'type': '職業類科'},
    '中壢家商(應用英語科)': {'points': 23, 'credits': 16, 'type': '職業類科'},
    '中壢家商(資料處理科)': {'points': 23, 'credits': 13, 'type': '職業類科'},
    '中壢家商(商業經營科)': {'points': 23, 'credits': 13, 'type': '職業類科'},
    '中壢家商(家政科)': {'points': 23, 'credits': 13, 'type': '職業類科'},
    '中壢家商(流行服飾)': {'points': 23, 'credits': 10, 'type': '職業類科'},
    '北科附工(電機科)': {'points': 25, 'credits': 16, 'type': '職業類科'},
    '北科附工(電子科)': {'points': 25, 'credits': 18, 'type': '職業類科'},
    '北科附工(畜產保健)': {'points': 25, 'credits': 16, 'type': '職業類科'},
    '北科附工(機械科)': {'points': 23, 'credits': 16, 'type': '職業類科'},
    '北科附工(化工科)': {'points': 23, 'credits': 16, 'type': '職業類科'},
    '北科附工(動力機械)': {'points': 23, 'credits': 14, 'type': '職業類科'},
    '北科附工(汽車科)': {'points': 23, 'credits': 12, 'type': '職業類科'},
    '北科附工(生物產業機電)': {'points': 23, 'credits': 13, 'type': '職業類科'},
    '北科附工(模具科)': {'points': 23, 'credits': 13, 'type': '職業類科'},
    '北科附工(農場經營科)': {'points': 23, 'credits': 12, 'type': '職業類科'},
    '北科附工(園藝科)': {'points': 23, 'credits': 12, 'type': '職業類科'},
}


# 當前邀請碼
current_invitation_code = ""

# 生成新邀請碼
def generate_invitation_code():
    global current_invitation_code
    current_invitation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# 初始化生成邀請碼
generate_invitation_code()

# 設定定時任務每小時更新邀請碼
scheduler = BackgroundScheduler()
scheduler.add_job(func=generate_invitation_code, trigger="interval", hours=1)
scheduler.start()

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/invitation_code_page')
def invitation_code_page():
    return render_template('invitation_code.html')

@app.route('/invitation_code')
def invitation_code():
    global current_invitation_code
    return jsonify({'invitation_code': current_invitation_code, 'timestamp': int(time.time())})


@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    invitation_code = data.get('invitation_code')

    if invitation_code != current_invitation_code:
        return jsonify({'error': '無效的邀請碼'}), 403

    chinese = data['chinese']
    english = data['english']
    math = data['math']
    science = data['science']
    social = data['social']
    composition = int(data['composition'])
    school_type = data['school_type']  # 從表單中取得學校類型選擇

    total_points = 0
    total_credits = 0

    subjects = [chinese, english, math, science, social]
    for score in subjects:
        total_points += score_to_points.get(score[0], 0)
        total_credits += score_to_credit.get(score, 0)

    total_points += score_to_points['作文'].get(composition, 0)

    eligible_schools = []
    for school, criteria in schools.items():
        if total_points >= criteria['points'] and total_credits >= criteria['credits']:
            if school_type == 'all' or criteria.get('type') == school_type:  # 根據學校類型選擇篩選學校
                eligible_schools.append(school)

    result = {
        'total_points': total_points,
        'total_credits': total_credits,
        'eligible_schools': eligible_schools
    }
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
