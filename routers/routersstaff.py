from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_conn

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/staff')
def show_staff():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''
            SELECT s.*, b.name as branch_name
            FROM Staff s
            LEFT JOIN Branch b ON s.branch_id = b.branch_id
            ORDER BY s.created_at DESC
        ''')
        staff = cur.fetchall()
        
        # جلب الفروع للاختيار
        cur.execute('SELECT branch_id, name FROM Branch')
        branches = cur.fetchall()
        
    except Exception as e:
        flash(f'خطأ في جلب البيانات: {str(e)}', 'error')
        staff = []
        branches = []
    finally:
        conn.close()
    
    return render_template('staff.html', staff=staff, branches=branches)

@staff_bp.route('/add_staff', methods=['POST'])
def add_staff():
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    position = request.form.get('position', '').strip()
    branch_id = request.form.get('branch_id')
    salary = request.form.get('salary', '').strip()
    
    # التحقق من صحة البيانات
    if not first_name or not last_name:
        flash('الاسم الأول والأخير مطلوبان!', 'error')
        return redirect(url_for('staff.show_staff'))
    
    if not position:
        flash('المنصب مطلوب!', 'error')
        return redirect(url_for('staff.show_staff'))
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO Staff (first_name, last_name, phone, email, position, branch_id, salary) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (first_name, last_name, phone if phone else None, email if email else None, 
                    position, branch_id if branch_id else None, float(salary) if salary else None))
        conn.commit()
        flash(f'تم إضافة الموظف "{first_name} {last_name}" بنجاح!', 'success')
    except Exception as e:
        flash(f'خطأ في إضافة الموظف: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('staff.show_staff'))

@staff_bp.route('/update_staff/<int:id>', methods=['POST'])
def update_staff(id):
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    position = request.form.get('position', '').strip()
    branch_id = request.form.get('branch_id')
    salary = request.form.get('salary', '').strip()
    
    # التحقق من صحة البيانات
    if not first_name or not last_name:
        flash('الاسم الأول والأخير مطلوبان!', 'error')
        return redirect(url_for('staff.show_staff'))
    
    if not position:
        flash('المنصب مطلوب!', 'error')
        return redirect(url_for('staff.show_staff'))
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('UPDATE Staff SET first_name=?, last_name=?, phone=?, email=?, position=?, branch_id=?, salary=? WHERE staff_id=?',
                    (first_name, last_name, phone if phone else None, email if email else None, 
                    position, branch_id if branch_id else None, float(salary) if salary else None, id))
        if cur.rowcount > 0:
            conn.commit()
            flash(f'تم تحديث الموظف "{first_name} {last_name}" بنجاح!', 'success')
        else:
            flash('الموظف غير موجود!', 'error')
    except Exception as e:
        flash(f'خطأ في تحديث الموظف: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('staff.show_staff'))

@staff_bp.route('/delete_staff/<int:id>')
def delete_staff(id):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # جلب اسم الموظف أولاً
        cur.execute('SELECT first_name, last_name FROM Staff WHERE staff_id=?', (id,))
        staff_member = cur.fetchone()
        
        if staff_member:
            cur.execute('DELETE FROM Staff WHERE staff_id=?', (id,))
            conn.commit()
            flash(f'تم حذف الموظف "{staff_member[0]} {staff_member[1]}" بنجاح!', 'success')
        else:
            flash('الموظف غير موجود!', 'error')
    except Exception as e:
        flash(f'خطأ في حذف الموظف: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('staff.show_staff'))