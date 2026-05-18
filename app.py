# app.py
from flask import Flask, render_template
from datetime import datetime, timedelta
from db import get_conn, init_db

# التصحيحات المطلوبة للـ imports - إزالة مجلد routers
from routers.routersbranch import branch_bp
from routers.routersclasses import classes_bp
from routers.routersparent import parent_bp
from routers.routerschild import child_bp
from routers.routersstaff import staff_bp
from routers.routersattendance import attendance_bp
from routers.routersfee import fee_bp


app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # مطلوب للـ flash messages

# register blueprints
app.register_blueprint(branch_bp)
app.register_blueprint(classes_bp)
app.register_blueprint(parent_bp)
app.register_blueprint(child_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(fee_bp)

# جعل دالة now متاحة في التمبليتات
@app.template_global()
def now():
    return datetime.now()

# Custom filter for relative time in Arabic
@app.template_filter('time_ago')
def time_ago_filter(timestamp):
    """Convert timestamp to relative time string in Arabic"""
    if not timestamp:
        return 'غير محدد'
    
    # Parse timestamp if it's a string
    if isinstance(timestamp, str):
        try:
            # Handle SQLite timestamp format: 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD HH:MM:SS.ssssss'
            timestamp_str = timestamp.split('.')[0]  # Remove microseconds if present
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"Error parsing timestamp: {timestamp}, Error: {e}")
            return 'غير محدد'
    
    now = datetime.now()
    diff = now - timestamp
    
    # Calculate time differences
    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    weeks = days / 7
    months = days / 30
    years = days / 365
    
    # Return appropriate Arabic string
    if seconds < 60:
        return 'الآن'
    elif minutes < 60:
        count = int(minutes)
        if count == 1:
            return 'منذ دقيقة واحدة'
        elif count == 2:
            return 'منذ دقيقتين'
        elif count <= 10:
            return f'منذ {count} دقائق'
        else:
            return f'منذ {count} دقيقة'
    elif hours < 24:
        count = int(hours)
        if count == 1:
            return 'منذ ساعة واحدة'
        elif count == 2:
            return 'منذ ساعتين'
        elif count <= 10:
            return f'منذ {count} ساعات'
        else:
            return f'منذ {count} ساعة'
    elif days < 7:
        count = int(days)
        if count == 1:
            return 'منذ يوم واحد'
        elif count == 2:
            return 'منذ يومين'
        elif count <= 10:
            return f'منذ {count} أيام'
        else:
            return f'منذ {count} يوم'
    elif weeks < 4:
        count = int(weeks)
        if count == 1:
            return 'منذ أسبوع واحد'
        elif count == 2:
            return 'منذ أسبوعين'
        else:
            return f'منذ {count} أسابيع'
    elif months < 12:
        count = int(months)
        if count == 1:
            return 'منذ شهر واحد'
        elif count == 2:
            return 'منذ شهرين'
        elif count <= 10:
            return f'منذ {count} أشهر'
        else:
            return f'منذ {count} شهر'
    else:
        count = int(years)
        if count == 1:
            return 'منذ سنة واحدة'
        elif count == 2:
            return 'منذ سنتين'
        else:
            return f'منذ {count} سنوات'

@app.route('/')
def index():
    # جلب إحصائيات سريعة للداشبورد
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        # إحصائيات سريعة
        cur.execute('SELECT COUNT(*) FROM Branch')
        branches_count = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM Class')
        classes_count = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM Child')
        children_count = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM Parent')
        parents_count = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM Staff')
        staff_count = cur.fetchone()[0]
        
        # أطفال حضروا اليوم
        cur.execute('SELECT COUNT(*) FROM Attendance WHERE date = DATE("now") AND status = "Present"')
        today_attendance = cur.fetchone()[0]
        
        # إجمالي الرسوم
        cur.execute('SELECT COUNT(*) FROM Fee')
        fees_count = cur.fetchone()[0]
        
        # جلب آخر 5 نشاطات
        cur.execute('''
            SELECT activity_type, description, timestamp
            FROM RecentActivity
            ORDER BY timestamp DESC
            LIMIT 5
        ''')
        recent_activities = cur.fetchall()
        
        stats = {
            'branches': branches_count,
            'classes': classes_count,
            'children': children_count,
            'parents': parents_count,
            'staff': staff_count,
            'today_attendance': today_attendance,
            'fees': fees_count
        }
    except Exception as e:
        # في حالة عدم وجود الجداول بعد
        print(f"خطأ في جلب الإحصائيات: {e}")
        stats = {
            'branches': 0,
            'classes': 0,
            'children': 0,
            'parents': 0,
            'staff': 0,
            'today_attendance': 0,
            'fees': 0
        }
        recent_activities = []
    
    conn.close()
    return render_template('index.html', stats=stats, recent_activities=recent_activities)

if __name__ == '__main__':
    # إنشاء قاعدة البيانات عند أول تشغيل
    init_db()
    app.run(debug=True)