import os
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, request
from dotenv import load_dotenv

from models import Branch, Class, Parent, Child, Staff, Attendance, Fee, User
from extensions import db, migrate

from routes.branch import branch_bp
from routes.classes import classes_bp
from routes.parent import parent_bp
from routes.child import child_bp
from routes.staff import staff_bp
from routes.attendance import attendance_bp
from routes.fee import fee_bp
from routes.auth import auth_bp

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nursery-dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)

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
    user_id = session['user_id']

    stats = {
        'branches': Branch.query.filter_by(user_id=user_id).count(),
        'classes': Class.query.filter_by(user_id=user_id).count(),
        'children': Child.query.filter_by(user_id=user_id, is_active=True).count(),
        'parents': Parent.query.filter_by(user_id=user_id).count(),
        'staff': Staff.query.filter_by(user_id=user_id, is_active=True).count(),
        'today_attendance': Attendance.query.filter_by(user_id=user_id, date=datetime.now().date()).count(),
        'fees': Fee.query.filter_by(user_id=user_id).count()
    }

    recent_activities = []

    latest_children = Child.query.filter_by(user_id=user_id).order_by(Child.created_at.desc()).limit(3).all()
    for child in latest_children:
        recent_activities.append({
            'icon': 'fa-child',
            'color': 'primary',
            'title': f'تم إضافة طفل: {child.first_name} {child.last_name}',
            'time': child.created_at
        })

    latest_parents = Parent.query.filter_by(user_id=user_id).order_by(Parent.created_at.desc()).limit(3).all()
    for parent in latest_parents:
        recent_activities.append({
            'icon': 'fa-users',
            'color': 'success',
            'title': f'تم إضافة ولي أمر: {parent.first_name} {parent.last_name}',
            'time': parent.created_at
        })

    latest_fees = Fee.query.filter_by(user_id=user_id).order_by(Fee.created_at.desc()).limit(3).all()
    for fee in latest_fees:
        recent_activities.append({
            'icon': 'fa-money-bill-wave',
            'color': 'warning',
            'title': 'تم إضافة رسوم جديدة',
            'time': fee.created_at
        })

    latest_attendance = Attendance.query.filter_by(user_id=user_id).order_by(Attendance.created_at.desc()).limit(3).all()
    for attendance in latest_attendance:
        recent_activities.append({
            'icon': 'fa-calendar-check',
            'color': 'info',
            'title': 'تم تسجيل حضور جديد',
            'time': attendance.created_at
        })

    recent_activities = sorted(
        recent_activities,
        key=lambda x: x['time'],
        reverse=True
    )[:6]

    return render_template(
        'index.html',
        stats=stats,
        recent_activities=recent_activities
    )

if __name__ == '__main__':
    app.run(debug=True)