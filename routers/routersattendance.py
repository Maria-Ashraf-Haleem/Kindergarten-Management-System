from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_conn, log_activity
from datetime import datetime, date

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance')
def show_attendance():
    conn = get_conn()
    cur = conn.cursor()
    try:
        # جلب سجلات الحضور مع معلومات الأطفال والكلاسات
        cur.execute('''
            SELECT a.*, 
                    c.first_name || " " || c.last_name as child_name,
                    cl.name as class_name,
                    b.name as branch_name
            FROM Attendance a
            LEFT JOIN Child c ON a.child_id = c.child_id
            LEFT JOIN Class cl ON c.class_id = cl.class_id
            LEFT JOIN Branch b ON cl.branch_id = b.branch_id
            ORDER BY a.date DESC, a.created_at DESC
            LIMIT 100
        ''')
        attendance_records = cur.fetchall()
        
        # جلب الأطفال النشطين للاختيار
        cur.execute('''
            SELECT c.child_id, 
                    c.first_name || " " || c.last_name as name,
                    cl.name as class_name
            FROM Child c
            LEFT JOIN Class cl ON c.class_id = cl.class_id
            WHERE c.is_active = 1
            ORDER BY c.first_name, c.last_name
        ''')
        children = cur.fetchall()
        
    except Exception as e:
        print(f"خطأ في جلب بيانات الحضور: {e}")
        flash(f'خطأ في جلب البيانات: {str(e)}', 'error')
        attendance_records = []
        children = []
    finally:
        conn.close()
    
    return render_template('attendance.html', 
                            attendance_records=attendance_records, 
                            children=children)

@attendance_bp.route('/add_attendance', methods=['POST'])
def add_attendance():
    child_id = request.form.get('child_id')
    date_str = request.form.get('date')
    status = request.form.get('status')
    check_in_time = request.form.get('check_in_time', '').strip()
    check_out_time = request.form.get('check_out_time', '').strip()
    notes = request.form.get('notes', '').strip()
    
    print(f"=== DEBUG: إضافة حضور ===")
    print(f"البيانات: child_id={child_id}, date={date_str}, status={status}")
    
    # التحقق من صحة البيانات
    if not child_id or not date_str or not status:
        flash('الطفل والتاريخ والحالة مطلوبة!', 'error')
        return redirect(url_for('attendance.show_attendance'))
    
    # تحويل القيم الفارغة إلى None
    check_in_time = check_in_time if check_in_time else None
    check_out_time = check_out_time if check_out_time else None
    notes = notes if notes else None
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        # التحقق من وجود سجل حضور لنفس الطفل في نفس التاريخ
        cur.execute('SELECT attendance_id FROM Attendance WHERE child_id = ? AND date = ?', 
                    (child_id, date_str))
        existing = cur.fetchone()
        
        if existing:
            flash('يوجد سجل حضور مسبق لهذا الطفل في نفس التاريخ!', 'error')
            return redirect(url_for('attendance.show_attendance'))
        
        # إضافة سجل الحضور
        cur.execute('''
            INSERT INTO Attendance (child_id, date, status, check_in_time, check_out_time, notes) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (child_id, date_str, status, check_in_time, check_out_time, notes))
        
        conn.commit()
        print(f"✅ تم تسجيل الحضور بنجاح")
        
        # جلب اسم الطفل للرسالة
        cur.execute('SELECT first_name || " " || last_name FROM Child WHERE child_id = ?', (child_id,))
        child = cur.fetchone()
        child_name = child[0] if child else "الطفل"
        
        flash(f'تم تسجيل حضور "{child_name}" بنجاح!', 'success')
        
        # تسجيل النشاط
        log_activity('attendance', 'تم تسجيل الحضور اليومي')
        
    except Exception as e:
        print(f"❌ خطأ في تسجيل الحضور: {e}")
        flash(f'خطأ في تسجيل الحضور: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('attendance.show_attendance'))

@attendance_bp.route('/bulk_attendance', methods=['POST'])
def bulk_attendance():
    """تسجيل حضور جماعي للأطفال"""
    date_str = request.form.get('date')
    child_ids = request.form.getlist('child_ids[]')
    statuses = request.form.getlist('statuses[]')
    check_in_times = request.form.getlist('check_in_times[]')
    notes_list = request.form.getlist('notes[]')
    
    if not date_str:
        flash('التاريخ مطلوب!', 'error')
        return redirect(url_for('attendance.show_attendance'))
    
    conn = get_conn()
    cur = conn.cursor()
    success_count = 0
    error_count = 0
    
    try:
        for i, child_id in enumerate(child_ids):
            if i < len(statuses) and statuses[i]:  # تخطي الأطفال بدون حالة محددة
                status = statuses[i]
                check_in_time = check_in_times[i] if i < len(check_in_times) and check_in_times[i] else None
                notes = notes_list[i] if i < len(notes_list) and notes_list[i] else None
                
                try:
                    # التحقق من وجود سجل مسبق
                    cur.execute('SELECT attendance_id FROM Attendance WHERE child_id = ? AND date = ?', 
                                (child_id, date_str))
                    existing = cur.fetchone()
                    
                    if not existing:
                        cur.execute('''
                            INSERT INTO Attendance (child_id, date, status, check_in_time, notes) 
                            VALUES (?, ?, ?, ?, ?)
                        ''', (child_id, date_str, status, check_in_time, notes))
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    print(f"خطأ في تسجيل حضور الطفل {child_id}: {e}")
                    error_count += 1
        
        if success_count > 0:
            conn.commit()
            flash(f'تم تسجيل حضور {success_count} طفل بنجاح!', 'success')
            # تسجيل النشاط
            log_activity('attendance', 'تم تسجيل الحضور اليومي')
        
        if error_count > 0:
            flash(f'فشل في تسجيل {error_count} من الأطفال (قد يكون لديهم سجلات مسبقة)', 'warning')
            
    except Exception as e:
        print(f"خطأ في التسجيل الجماعي: {e}")
        flash(f'خطأ في التسجيل الجماعي: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('attendance.show_attendance'))

@attendance_bp.route('/update_attendance/<int:id>', methods=['POST'])
def update_attendance(id):
    child_id = request.form.get('child_id')
    date_str = request.form.get('date')
    status = request.form.get('status')
    check_in_time = request.form.get('check_in_time', '').strip()
    check_out_time = request.form.get('check_out_time', '').strip()
    notes = request.form.get('notes', '').strip()
    
    # التحقق من صحة البيانات
    if not child_id or not date_str or not status:
        flash('جميع الحقول الأساسية مطلوبة!', 'error')
        return redirect(url_for('attendance.show_attendance'))
    
    # تحويل القيم الفارغة إلى None
    check_in_time = check_in_time if check_in_time else None
    check_out_time = check_out_time if check_out_time else None
    notes = notes if notes else None
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''
            UPDATE Attendance 
            SET child_id=?, date=?, status=?, check_in_time=?, check_out_time=?, notes=?
            WHERE attendance_id=?
        ''', (child_id, date_str, status, check_in_time, check_out_time, notes, id))
        
        if cur.rowcount > 0:
            conn.commit()
            
            # جلب اسم الطفل للرسالة
            cur.execute('SELECT first_name || " " || last_name FROM Child WHERE child_id = ?', (child_id,))
            child = cur.fetchone()
            child_name = child[0] if child else "الطفل"
            
            flash(f'تم تحديث حضور "{child_name}" بنجاح!', 'success')
        else:
            flash('سجل الحضور غير موجود!', 'error')
            
    except Exception as e:
        flash(f'خطأ في تحديث الحضور: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('attendance.show_attendance'))

@attendance_bp.route('/delete_attendance/<int:id>')
def delete_attendance(id):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # جلب معلومات السجل أولاً للرسالة
        cur.execute('''
            SELECT c.first_name || " " || c.last_name, a.date 
            FROM Attendance a
            LEFT JOIN Child c ON a.child_id = c.child_id
            WHERE a.attendance_id = ?
        ''', (id,))
        record = cur.fetchone()
        
        if record:
            cur.execute('DELETE FROM Attendance WHERE attendance_id = ?', (id,))
            conn.commit()
            flash(f'تم حذف سجل حضور "{record[0]}" بتاريخ "{record[1]}" بنجاح!', 'success')
        else:
            flash('سجل الحضور غير موجود!', 'error')
            
    except Exception as e:
        flash(f'خطأ في حذف سجل الحضور: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('attendance.show_attendance'))

@attendance_bp.route('/attendance_report')
def attendance_report():
    """تقرير مفصل للحضور"""
    conn = get_conn()
    cur = conn.cursor()
    
    # الحصول على معاملات الفلترة
    start_date = request.args.get('start_date', date.today().strftime('%Y-%m-01'))
    end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
    child_id = request.args.get('child_id')
    class_id = request.args.get('class_id')
    
    try:
        # بناء الاستعلام الديناميكي
        query = '''
            SELECT a.*, 
                    c.first_name || " " || c.last_name as child_name,
                    cl.name as class_name,
                    b.name as branch_name
            FROM Attendance a
            LEFT JOIN Child c ON a.child_id = c.child_id
            LEFT JOIN Class cl ON c.class_id = cl.class_id
            LEFT JOIN Branch b ON cl.branch_id = b.branch_id
            WHERE a.date BETWEEN ? AND ?
        '''
        params = [start_date, end_date]
        
        if child_id:
            query += " AND a.child_id = ?"
            params.append(child_id)
            
        if class_id:
            query += " AND c.class_id = ?"
            params.append(class_id)
            
        query += " ORDER BY a.date DESC, c.first_name"
        
        cur.execute(query, params)
        attendance_records = cur.fetchall()
        
        # إحصائيات الفترة
        cur.execute('''
            SELECT status, COUNT(*) as count 
            FROM Attendance 
            WHERE date BETWEEN ? AND ?
            GROUP BY status
        ''', (start_date, end_date))
        status_summary = cur.fetchall()
        
        # جلب الأطفال والكلاسات للفلاتر
        cur.execute('SELECT child_id, first_name || " " || last_name as name FROM Child WHERE is_active = 1')
        children = cur.fetchall()
        
        cur.execute('SELECT class_id, name FROM Class ORDER BY name')
        classes = cur.fetchall()
        
    except Exception as e:
        print(f"خطأ في تقرير الحضور: {e}")
        attendance_records = []
        status_summary = []
        children = []
        classes = []
    finally:
        conn.close()
    
    return render_template('attendance_report.html',
                            attendance_records=attendance_records,
                            status_summary=status_summary,
                            children=children,
                            classes=classes,
                            start_date=start_date,
                            end_date=end_date,
                            selected_child=child_id,
                            selected_class=class_id)