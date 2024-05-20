from flask import Flask, render_template, request, redirect, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from routes.student_routes import student_routes
from routes.admin_routes import admin_routes
from datetime import datetime
from flask import Flask, render_template, request, redirect, session, flash  # 導入 flash
import pandas as pd
from flask_bcrypt import Bcrypt
from datetime import datetime, time


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)



class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    math = db.Column(db.Integer)
    science = db.Column(db.Integer)
    last_login = db.Column(db.DateTime, nullable=True)  # 新增最近一次登入的時間欄位
    leaves = db.relationship('Leave', backref='student', lazy=True)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)  # 添加外键引用到Student表
    subject = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer)



class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.String(20), nullable=True)  # 将字段设为可为空
    reason = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')


class AccessTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String(20), nullable=False)
    end_time = db.Column(db.String(20), nullable=False)



# 创建数据库表格
with app.app_context():
    db.create_all()

# 注册蓝图
app.register_blueprint(student_routes)
app.register_blueprint(admin_routes)

# 首页
@app.route('/')
def index():
    return render_template('index.html')

def access_time_to_dict(access_time):
    return {'start_time': access_time.start_time, 'end_time': access_time.end_time}

# 學生登入
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # 管理員登入
    admin = Admin.query.filter_by(username=username).first()
    if admin and bcrypt.check_password_hash(admin.password, password):
        session['username'] = username
        return redirect('/dashboard_admin')
    
    # 學生登入
    student = Student.query.filter_by(username=username).first()
    if student and bcrypt.check_password_hash(student.password, password):
        access_time = AccessTime.query.first()
        current_time = datetime.now().time()  # 獲取當前時間的 time 對象
        start_time = datetime.strptime(access_time.start_time, "%H:%M").time()  # 將字符串轉換為時間對象
        end_time = datetime.strptime(access_time.end_time, "%H:%M").time()  # 將字符串轉換為時間對象
        if access_time and start_time <= current_time <= end_time:
            session['username'] = username
            student.last_login = datetime.now()  # 更新最近一次登入的時間
            db.session.commit()  # 提交更新到資料庫
            return redirect('/dashboard_student')
        else:
            return render_template('student_login.html', error="當前時間尚未開放", access_time=None)
    
    return render_template('student_login.html', error="無效的用戶名或密碼", access_time=None)
# 匯出成績摘要
@app.route('/export_grade_summary', methods=['GET'])
def export_grade_summary():
    if 'username' in session:
        admin = Admin.query.filter_by(username=session['username']).first()
        if admin:
            grades = db.session.query(Grade, Student).join(Student).all()
            df = pd.DataFrame([(grade.student.username, grade.subject, grade.score) for grade, _ in grades], 
                              columns=['学生', '科目', '成绩'])
            file_path = 'grades.xlsx'
            df.to_excel(file_path, index=False)
            return send_file(file_path, as_attachment=True)
    return redirect('/')




# 学生仪表板
@app.route('/dashboard_student')
def dashboard_student():
    if 'username' in session:
        student = Student.query.filter_by(username=session['username']).first()
        if student:
            student_grades = Grade.query.filter_by(student_id=student.id).all()
            return render_template('dashboard_student.html', username=session['username'], grades=student_grades, student=student)
    return redirect('/')


# 管理员仪表板
@app.route('/dashboard_admin')
def dashboard_admin():
    if 'username' in session:
        admin = Admin.query.filter_by(username=session['username']).first()
        if admin:
            students = Student.query.all()
            access_time = AccessTime.query.first()  # 获取管理员设置的登录时间
            return render_template('dashboard_admin.html', username=session['username'], students=students, access_time=access_time)
    return redirect('/')

@app.route('/set_student_login_time', methods=['POST'])
def set_student_login_time():
    if 'username' in session:
        admin = Admin.query.filter_by(username=session['username']).first()
        if admin:
            try:
                start_time = request.form['start_time']
                end_time = request.form['end_time']
                # 在数据库中保存管理员设置的学生登录时间
                access_time = AccessTime.query.first()
                if access_time:
                    access_time.start_time = start_time
                    access_time.end_time = end_time
                else:
                    access_time = AccessTime(start_time=start_time, end_time=end_time)
                    db.session.add(access_time)
                db.session.commit()
                print("学生登录时间已设置：", start_time, "-", end_time)
                return redirect('/dashboard_admin')
            except Exception as e:
                print("設定學生登入時間時發生錯誤:", e)
                return redirect('/dashboard_admin')
    return redirect('/dashboard_admin')

# 設定學生登入時間頁面路由
@app.route('/set_login_time_page')
def set_login_time_page():
    return render_template('set_access_time.html')

# 設定學生登入時間的路由
@app.route('/set_login_time', methods=['GET', 'POST'])
def set_login_time():
    if request.method == 'POST':
        # 在這裡處理提交的表單數據並設定學生登入時間
        # 這裡只是一個示例
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        # 在這裡處理設定學生登入時間的邏輯

        return redirect('/dashboard_admin')  # 或者重定向到其他頁面

    # 如果是GET請求，則渲染設定學生登入時間的頁面
    return render_template('set_login_time.html')


# 学生登入
@app.route('/student_login')
def student_login():
   return render_template('student_login.html')



# 登出
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

# 学生注册
@app.route('/register_student_page')
def register_student_page():
    return render_template('register_student_page.html')

@app.route('/register_student', methods=['POST'])
def register_student():
    username = request.form['username']
    password = request.form['password']
    if not Student.query.filter_by(username=username).first():
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_student = Student(username=username, password=hashed_password)
        db.session.add(new_student)
        db.session.commit()
        session['username'] = username
        return redirect('/dashboard_student')
    else:
        return "Student account already exists"

# 管理员注册
@app.route('/register_admin_page')
def register_admin_page():
    return render_template('register_admin_page.html')

@app.route('/register_admin', methods=['POST'])
def register_admin():
    username = request.form['username']
    password = request.form['password']
    if not Admin.query.filter_by(username=username).first():
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_admin = Admin(username=username, password=hashed_password)
        db.session.add(new_admin)
        db.session.commit()
        session['username'] = username
        return redirect('/dashboard_admin')
    else:
        return "Admin account already exists"
    

# 核准请假
@app.route('/approve_leave', methods=['POST'])
def approve_leave():
    if 'username' in session:
        admin = Admin.query.filter_by(username=session['username']).first()
        if admin:
            leave_id = request.form['leave_id']
            leave = Leave.query.get(leave_id)
            if leave:
                leave.status = 'approved'  # 更新请假状态为已核准
                db.session.commit()
                return redirect('/dashboard_admin')
    return redirect('/dashboard_admin')

# 显示成绩数据总表页面
@app.route('/grade_summary')
def grade_summary():
    if 'username' in session:
        admin = Admin.query.filter_by(username=session['username']).first()
        if admin:
            grades = db.session.query(Grade, Student).join(Student).all()
            return render_template('grade_summary.html', grades=grades)
    return redirect('/')

# 提交请假申请
@app.route('/submit_leave', methods=['POST'])
def submit_leave():
    if 'username' in session:
        student = Student.query.filter_by(username=session['username']).first()
        if student:
            # 获取表单数据
            leave_date = request.form['leave_date']
            leave_reason = request.form['leave_reason']
            
            # 创建请假记录并保存到数据库
            new_leave = Leave(student_id=student.id, date=leave_date, reason=leave_reason)
            db.session.add(new_leave)
            db.session.commit()
            
            # 重定向到学生仪表板页面
            return redirect('/dashboard_student')
    
    # 如果未登录或其他原因导致无法提交请假申请，则重定向到首页
    return redirect('/')





# 输入成绩
@app.route('/input_grades', methods=['GET', 'POST'])
def input_grades():
    if 'username' in session:
        admin = Admin.query.filter_by(username=session['username']).first()
        if admin:
            if request.method == 'POST':
                for student in Student.query.all():
                    math_score = request.form.get(f"{student.id}_math")
                    science_score = request.form.get(f"{student.id}_science")
                    if math_score and science_score:
                        new_grade_math = Grade(student_id=student.id, subject='Math', score=math_score)
                        new_grade_science = Grade(student_id=student.id, subject='Science', score=science_score)
                        db.session.add(new_grade_math)
                        db.session.add(new_grade_science)
                db.session.commit()
                flash('成绩已成功提交', 'success')  # 添加成功消息
                return redirect('/dashboard_admin')
            return render_template('input_grades.html', students=Student.query.all())
    return redirect('/dashboard_admin')

# 注册学生列表
@app.route('/registered_students')
def registered_students():
    if 'username' in session:
        admin = Admin.query.filter_by(username=session['username']).first()
        if admin:
            return render_template('registered_students.html', students=Student.query.all())
    return redirect('/dashboard_admin')

# 添加科目
@app.route('/add_subject', methods=['POST'])
def add_subject():
    if 'username' in session:
        admin = Admin.query.filter_by(username=session['username']).first()
        if admin:
            subject_name = request.form['subject_name']
            if not Grade.query.filter_by(subject=subject_name).first():
                for student in Student.query.all():
                    new_grade = Grade(student_id=student.id, subject=subject_name)
                    db.session.add(new_grade)
                db.session.commit()
                return redirect('/dashboard_admin')
            return "Subject already exists"
    return redirect('/dashboard_admin')



# 添加学生账号密码
@app.route('/add_student_account', methods=['POST'])
def add_student_account():
    if 'username' in session:
        admin = Admin.query.filter_by(username=session['username']).first()
        if admin:
            username = request.form['username']
            password = request.form['password']
            if not Student.query.filter_by(username=username).first():
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                new_student = Student(username=username, password=hashed_password)
                db.session.add(new_student)
                db.session.commit()
                return redirect('/dashboard_admin')
            return "Student account already exists"
    return redirect('/dashboard_admin')

# 新增学生页面
@app.route('/add_student_page')
def add_student_page():
    if 'username' in session:
        admin = Admin.query.filter_by(username=session['username']).first()
        if admin:
            return render_template('add_student_page.html')
    return redirect('/dashboard_admin')

# Change Password for Students
@app.route('/change_password', methods=['POST'])
def change_password():
    if 'username' in session:
        student = Student.query.filter_by(username=session['username']).first()
        if student:
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            # Check if the current password matches the one stored in the database
            if bcrypt.check_password_hash(student.password, current_password):
                # Check if the new password and confirm password match
                if new_password == confirm_password:
                    # Hash the new password and update it in the database
                    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                    student.password = hashed_password
                    db.session.commit()
                    flash('Password changed successfully', 'success')
                    return redirect('/dashboard_student')
                else:
                    flash('New password and confirm password do not match', 'error')
                    return redirect('/dashboard_student')
            else:
                flash('Current password is incorrect', 'error')
                return redirect('/dashboard_student')
    return redirect('/')


if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000)
