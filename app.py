from flask import Flask, render_template, jsonify, request, redirect, url_for, session, send_file
from datetime import datetime, timedelta
import random
import os
from io import BytesIO
import json
from functools import wraps
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__, 
    static_folder='static',
    static_url_path='/static',
    template_folder='templates'
)
app.secret_key = 'your-secret-key-123'  # 用于session加密

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 测试账号
TEST_CREDENTIALS = {
    "email": "test@example.com",
    "password": "test123"
}

# 模拟数据
MOCK_USER = {
    "name": "Jason Miller",
    "email": "jason.miller@example.com",
    "location": "Dublin, Ireland",
    "occupation": "Software Engineer",
    "health_stats": {
        "bmi": 23.5,
        "weight": 75,
        "target_weight": 78,
        "weekly_workouts": 4
    }
}

MOCK_REMINDERS = [
    {
        "id": 1,
        "type": "medication",
        "time": "08:00",
        "description": "Protein Supplement",
        "icon": "💊",
        "active": True
    },
    {
        "id": 2,
        "type": "exercise",
        "time": "18:00",
        "description": "Gym Workout",
        "icon": "🏋️",
        "active": True
    },
    {
        "id": 3,
        "type": "appointment",
        "time": "09:00",
        "description": "Doctor Appointment",
        "icon": "👨‍⚕️",
        "active": True
    }
]

MOCK_HEALTH_LOG = {
    "symptoms": ["Headache", "Fatigue", "Muscle soreness"],
    "exercises": ["Running", "Walking", "Gym workout", "Swimming"],
    "medications": ["Vitamin D", "Protein Powder", "Pre-workout"],
    "diet": ["Fruits", "Vegetables", "Protein", "Whole grains"]
}

# Mock user data for demonstration
class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

# Mock user database
users = {
    'user@example.com': User(1, 'user', 'user@example.com', 'password')
}

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 路由
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = users.get(email)
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    # Mock user data for demonstration
    user = {
        'name': 'Bill Smith',
        'email': 'bill.smith@example.com',
        'age': 35,
        'gender': 'Male',
        'height': 175,
        'weight': 70,
        'target_weight': 68,
        'blood_type': 'A+',
        'medical_history': ['Hypertension', 'Type 2 Diabetes'],
        'allergies': ['Penicillin'],
        'medications': ['Metformin', 'Lisinopril'],
        'emergency_contact': {
            'name': 'Jane Smith',
            'relationship': 'Spouse',
            'phone': '+1 234 567 8900'
        },
        'health_stats': {
            'weekly_workouts': 4,
            'weight': 70,
            'bmi': 22.9
        },
        'health_goals': {
            'weekly_exercise': 300,
            'daily_steps': 10000,
            'sleep_hours': 8
        }
    }
    return render_template('profile.html', user=user, active_page='profile')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', 
        user=MOCK_USER, 
        reminders=MOCK_REMINDERS[:3],
        active_page='dashboard'
    )

@app.route('/daily-log')
@login_required
def daily_log():
    return render_template('daily-log.html', 
        user=MOCK_USER,
        health_log=MOCK_HEALTH_LOG,
        active_page='daily-log'
    )

@app.route('/reminders')
def reminders():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('reminders.html', 
        user=MOCK_USER,
        reminders=MOCK_REMINDERS,
        active_page='reminders'
    )

@app.route('/insights')
@login_required
def insights():
    return render_template('insights.html', 
        user=MOCK_USER,
        active_page='insights'
    )

@app.route('/summary')
def summary():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('summary.html', 
        user=MOCK_USER,
        is_premium=False,
        active_page='summary'
    )

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # 获取表单数据
        full_name = request.form.get('fullName')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # 这里你通常会验证数据并将用户信息存储到数据库中
        # 由于这是一个演示，我们只是返回成功消息
        
        # 检查是否是AJAX请求
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': 'Registration successful! Please log in.'
            })
        
        # 如果是普通表单提交，重定向到登录页
        return redirect(url_for('login'))
        
    return render_template('signup.html')

# API 端点
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if email == TEST_CREDENTIALS['email'] and password == TEST_CREDENTIALS['password']:
        session['user_email'] = email
        return jsonify({
            "success": True,
            "redirect": url_for('dashboard')
        })
    else:
        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

@app.route('/api/add-reminder', methods=['POST'])
def api_add_reminder():
    reminder = request.json
    reminder['id'] = len(MOCK_REMINDERS) + 1
    MOCK_REMINDERS.append(reminder)
    return jsonify({"success": True, "reminder": reminder})

@app.route('/api/save-health-log', methods=['POST'])
def api_save_health_log():
    # 模拟保存健康日志
    return jsonify({"success": True})

@app.route('/premium')
def premium():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('premium.html', 
        user=MOCK_USER,
        active_page='premium'
    )

@app.route('/api/health-report')
def generate_health_report():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # 这里应该生成一个专业的PDF报告
    # 为演示目的，我们返回一个简单的文本文件
    report = BytesIO()
    report.write(b"CoreWell Professional Health Report\n\n")
    report.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n".encode())
    report.seek(0)
    
    return send_file(
        report,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='CoreWell-Health-Report.pdf'
    )

@app.route('/api/report-content')
def get_report_content():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # 这里应该返回专业的健康报告HTML内容
    report_content = """
    <div style="padding: 1rem;">
        <h3 style="color: #333; margin-bottom: 1rem;">Professional Health Analysis</h3>
        
        <div style="margin-bottom: 2rem;">
            <h4 style="color: #666;">Exercise Performance</h4>
            <p>Your exercise routine shows excellent consistency with an average of 45 minutes per session. 
            The intensity distribution is optimal: 60% moderate, 30% high, and 10% low intensity. 
            Your cardiovascular fitness score has improved by 15% over the past month.</p>
        </div>
        
        <div style="margin-bottom: 2rem;">
            <h4 style="color: #666;">Sleep Quality Analysis</h4>
            <p>Sleep patterns indicate good sleep hygiene with an average of 7.5 hours per night. 
            Deep sleep ratio of 25% is within the optimal range. REM sleep could be improved through 
            better evening routine management.</p>
        </div>
        
        <div style="margin-bottom: 2rem;">
            <h4 style="color: #666;">Blood Glucose Management</h4>
            <p>Blood glucose levels are well-maintained with 92% time in range (4.5-7.0 mmol/L). 
            Post-meal spikes are minimal, suggesting effective meal timing and composition.</p>
        </div>
        
        <div style="margin-bottom: 2rem;">
            <h4 style="color: #666;">Emotional Wellbeing</h4>
            <p>Emotional resilience score is strong at 85/100. Stress management techniques are 
            effective, with positive mood states dominating 60% of the time. Consider implementing 
            additional mindfulness practices for even better results.</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px;">
            <h4 style="color: #666;">Professional Recommendations</h4>
            <ul style="color: #555; line-height: 1.6;">
                <li>Increase high-intensity intervals to 2 sessions per week</li>
                <li>Implement a 20-minute wind-down routine before bed</li>
                <li>Add more fiber-rich foods to breakfast</li>
                <li>Consider afternoon meditation sessions</li>
            </ul>
        </div>
    </div>
    """
    
    return report_content

@app.route('/notifications')
@login_required
def notifications():
    return render_template('notifications.html')

@app.route('/api/health-metrics', methods=['GET'])
@login_required
def get_health_metrics():
    # Mock health metrics data
    metrics = {
        'heart_rate': 75,
        'blood_pressure': {'systolic': 120, 'diastolic': 80},
        'blood_oxygen': 98,
        'temperature': 36.6,
        'steps': 8432,
        'calories': 2100,
        'sleep': 7.5
    }
    return jsonify(metrics)

@app.route('/api/daily-log', methods=['POST'])
@login_required
def save_daily_log():
    data = request.json
    # Here you would typically save the data to a database
    return jsonify({'status': 'success'})

@app.route('/api/health-report', methods=['GET'])
@login_required
def get_health_report():
    # Mock health report data
    report = {
        'summary': 'Your health metrics are within normal ranges.',
        'recommendations': [
            'Consider increasing daily water intake',
            'Try to get more sleep',
            'Take regular breaks during work'
        ],
        'metrics_trend': {
            'heart_rate': 'stable',
            'blood_pressure': 'improving',
            'sleep': 'needs attention'
        }
    }
    return jsonify(report)

@app.route('/ask-doctor')
@login_required
def ask_doctor():
    return render_template('ask-doctor.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000) 