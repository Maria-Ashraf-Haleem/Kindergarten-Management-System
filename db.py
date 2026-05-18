# db.py
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'kindergarten.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # access columns by name in templates
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    """إنشاء جداول قاعدة البيانات"""
    conn = get_conn()
    cur = conn.cursor()
    
    # جدول الفروع
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Branch (
            branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول الكلاسات
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Class (
            class_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            branch_id INTEGER,
            max_capacity INTEGER DEFAULT 25,
            age_group TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (branch_id) REFERENCES Branch(branch_id) ON DELETE CASCADE
        )
    ''')
    
    # جدول أولياء الأمور
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Parent (
            parent_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            emergency_contact TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول الأطفال
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Child (
            child_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth DATE,
            gender TEXT CHECK(gender IN ('Male', 'Female')),
            parent_id INTEGER,
            class_id INTEGER,
            medical_info TEXT,
            enrollment_date DATE DEFAULT CURRENT_DATE,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES Parent(parent_id) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES Class(class_id) ON DELETE SET NULL
        )
    ''')
    
    # جدول الموظفين
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            position TEXT NOT NULL,
            branch_id INTEGER,
            phone TEXT,
            email TEXT,
            hire_date DATE DEFAULT CURRENT_DATE,
            salary DECIMAL(10,2),
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (branch_id) REFERENCES Branch(branch_id) ON DELETE SET NULL
        )
    ''')
    
    # جدول المواد
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Subject (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول حضور الأطفال
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id INTEGER,
            date DATE NOT NULL,
            status TEXT CHECK(status IN ('Present', 'Absent', 'Late')) DEFAULT 'Present',
            check_in_time TIME,
            check_out_time TIME,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (child_id) REFERENCES Child(child_id) ON DELETE CASCADE
        )
    ''')
    
    # جدول حضور الموظفين
    cur.execute('''
        CREATE TABLE IF NOT EXISTS StaffAttendance (
            staff_attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER,
            date DATE NOT NULL,
            check_in_time TIME,
            check_out_time TIME,
            status TEXT CHECK(status IN ('Present', 'Absent', 'Late', 'Half Day')) DEFAULT 'Present',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (staff_id) REFERENCES Staff(staff_id) ON DELETE CASCADE
        )
    ''')
    
    # جدول الرسوم
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Fee (
            fee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id INTEGER,
            amount DECIMAL(10,2) NOT NULL,
            due_date DATE,
            paid_date DATE,
            payment_method TEXT,
            status TEXT CHECK(status IN ('Pending', 'Paid', 'Overdue')) DEFAULT 'Pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (child_id) REFERENCES Child(child_id) ON DELETE CASCADE
        )
    ''')
    # جدول المستخدمين
    cur.execute('''
        CREATE TABLE IF NOT EXISTS User (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول التخرج
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Graduation (
            graduation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id INTEGER,
            graduation_date DATE NOT NULL,
            certificate_issued BOOLEAN DEFAULT 0,
            final_grade TEXT,
            comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (child_id) REFERENCES Child(child_id) ON DELETE CASCADE
        )
    ''')
    
    # جدول النشاطات الحديثة
    cur.execute('''
        CREATE TABLE IF NOT EXISTS RecentActivity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_type TEXT NOT NULL,
            description TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ تم إنشاء قاعدة البيانات بنجاح!")

def log_activity(activity_type, description):
    """
    Helper function to log activities to the RecentActivity table
    
    Args:
        activity_type: Type of activity (e.g., 'new_child', 'attendance', 'payment')
        description: Description of the activity in Arabic
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO RecentActivity (activity_type, description, timestamp)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (activity_type, description))
        conn.commit()
    except Exception as e:
        print(f"خطأ في تسجيل النشاط: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()