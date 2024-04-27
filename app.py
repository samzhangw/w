from flask import Flask, render_template, request, redirect, session
from flask_bcrypt import Bcrypt
from PIL import Image, ImageDraw, ImageFont
import random
import io
import base64

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
bcrypt = Bcrypt(app)

# 學生帳號和密碼
students = {
    'student1': {'password': '$2b$12$6Wz.ZzCyAHhHsmX5YIscbOw/tCrxgHXTrrlK0iy1ZWDh68l0PFt0W', 'math': None, 'science': None},
    'student2': {'password': '$2b$12$DVeY5C55F0F/SauPSdNBZubLPVZoDh7eCdqF41IRmUf.I9lgfE8Fq', 'math': None, 'science': None}
}

# 管理員帳號和密碼
admins = {}

# 成績
grades = {
    'student1': {'math': 90, 'science': 85},
    'student2': {'math': 80, 'science': 75}
}

# 生成驗證碼
def generate_captcha():
    width, height = 200, 50
    image = Image.new('RGB', (width, height), color = (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('arial.ttf', 30)
    captcha = ''.join(random.choices('0123456789', k=6))
    draw.text((10, 10), captcha, font=font, fill=(0, 0, 0))
    # 將圖片轉換為Base64格式
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return captcha, img_str

# 首頁
@app.route('/')
def index():
    return render_template('index.html')

# 登入
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    # 學生登入
    if username in students and bcrypt.check_password_hash(students[username]['password'], password):
        session['username'] = username
        return redirect('/dashboard_student')
    # 管理員登入
    elif username in admins and bcrypt.check_password_hash(admins[username], password):
        session['username'] = username
        return redirect('/dashboard_admin')
    else:
        return render_template('index.html', error="Invalid username or password")

# 學生儀表板
@app.route('/dashboard_student')
def dashboard_student():
    if 'username' in session and session['username'] in students:
        return render_template('dashboard_student.html', username=session['username'], grades=students[session['username']])
    return redirect('/')

# 管理員儀表板
@app.route('/dashboard_admin')
def dashboard_admin():
    if 'username' in session and session['username'] in admins:
        return render_template('dashboard_admin.html', username=session['username'], students=students, grades=grades)
    return redirect('/')

# 登出
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

# 學生註冊
@app.route('/register_student', methods=['POST'])
def register_student():
    username = request.form['username']
    password = request.form['password']
    if username not in students:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        students[username] = {'password': hashed_password, 'math': None, 'science': None}
        session['username'] = username
        return redirect('/dashboard_student')
    else:
        return "Student account already exists"

# 學生註冊頁面
@app.route('/register_student_page')
def register_student_page():
    return render_template('register_student.html')

# 管理員註冊
@app.route('/register_admin', methods=['POST'])
def register_admin():
    username = request.form['username']
    password = request.form['password']
    # 檢查驗證碼
    entered_captcha = request.form['captcha']
    if entered_captcha != session['captcha']:
        return "Invalid captcha"

    if username not in admins:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        admins[username] = hashed_password
        session['username'] = username
        return redirect('/dashboard_admin')
    else:
        return "Admin account already exists"

# 管理員註冊頁面
@app.route('/register_admin_page')
def register_admin_page():
    captcha, img_str = generate_captcha()
    session['captcha'] = captcha
    return render_template('register_admin.html', captcha=img_str)

# 成績輸入
@app.route('/input_grades', methods=['POST'])
def input_grades():
    for student in students:
        students[student]['math'] = request.form['math_' + student]
        students[student]['science'] = request.form['science_' + student]
    return redirect('/dashboard_admin')

if __name__ == '__main__':
    app.run(debug=True)
