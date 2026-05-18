import os
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, request
from dotenv import load_dotenv

from extensions import db, migrate

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nursery-dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)

# مهم: استيراد الموديلز عشان Flask-Migrate يشوف الجداول
from models import Branch, Class, Parent, Child, Staff, Attendance, Fee, User


# imports بتاعة الروترز
from routers.routersbranch import branch_bp
from routers.routersclasses import classes_bp
from routers.routersparent import parent_bp
from routers.routerschild import child_bp
from routers.routersstaff import staff_bp
from routers.routersattendance import attendance_bp
from routers.routersfee import fee_bp
from routers.auth import auth_bp


app.register_blueprint(branch_bp)
app.register_blueprint(classes_bp)
app.register_blueprint(parent_bp)
app.register_blueprint(child_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(fee_bp)
app.register_blueprint(auth_bp)


@app.template_global()
def now():
    return datetime.now()


@app.template_filter('time_ago')
def time_ago_filter(timestamp):
    if not timestamp:
        return 'غير محدد'

    if isinstance(timestamp, str):
        try:
            timestamp = datetime.strptime(timestamp.split('.')[0], '%Y-%m-%d %H:%M:%S')
        except Exception:
            return 'غير محدد'

    diff = datetime.now() - timestamp
    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24

    if seconds < 60:
        return 'الآن'
    elif minutes < 60:
        return f'منذ {int(minutes)} دقيقة'
    elif hours < 24:
        return f'منذ {int(hours)} ساعة'
    else:
        return f'منذ {int(days)} يوم'

@app.template_filter('format_date')
def format_date(value):
    if not value:
        return 'غير محدد'

    try:
        return value.strftime('%Y-%m-%d')
    except AttributeError:
        return str(value)[:10]


@app.template_filter('input_date')
def input_date(value):
    if not value:
        return ''

    try:
        return value.strftime('%Y-%m-%d')
    except AttributeError:
        return str(value)[:10]


@app.template_filter('input_time')
def input_time(value):
    if not value:
        return ''

    try:
        return value.strftime('%H:%M')
    except AttributeError:
        return str(value)[:5]

@app.before_request
def require_login():
    if request.endpoint is None:
        return

    allowed_endpoints = [
        'auth.login',
        'auth.signup',
        'static'
    ]

    if request.endpoint in allowed_endpoints or request.endpoint.startswith('static'):
        return

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))


@app.route('/')
def index():
    stats = {
        'branches': Branch.query.count(),
        'classes': Class.query.count(),
        'children': Child.query.filter_by(is_active=True).count(),
        'parents': Parent.query.count(),
        'staff': Staff.query.filter_by(is_active=True).count(),
        'today_attendance': Attendance.query.filter_by(date=datetime.now().date()).count(),
        'fees': Fee.query.count()
    }

    recent_activities = []

    return render_template('index.html', stats=stats, recent_activities=recent_activities)


if __name__ == '__main__':
    app.run(debug=True)