from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_conn

branch_bp = Blueprint('branch', __name__)

@branch_bp.route('/branches')
def show_branches():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''
            SELECT b.*, 
                   COUNT(DISTINCT c.class_id) as classes_count,
                   COUNT(DISTINCT s.staff_id) as staff_count
            FROM Branch b
            LEFT JOIN Class c ON b.branch_id = c.branch_id
            LEFT JOIN Staff s ON b.branch_id = s.branch_id
            GROUP BY b.branch_id
            ORDER BY b.created_at DESC
        ''')
        branches = cur.fetchall()
        
    except Exception as e:
        flash(f'خطأ في جلب البيانات: {str(e)}', 'error')
        branches = []
    finally:
        conn.close()
    
    return render_template('branch.html', branches=branches)

@branch_bp.route('/add_branch', methods=['POST'])
def add_branch():
    name = request.form.get('name', '').strip()
    address = request.form.get('address', '').strip()
    phone = request.form.get('phone', '').strip()
    
    # التحقق من صحة البيانات
    if not name:
        flash('اسم الفرع مطلوب!', 'error')
        return redirect(url_for('branch.show_branches'))
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        # التحقق من عدم وجود فرع بنفس الاسم
        cur.execute('SELECT name FROM Branch WHERE name = ?', (name,))
        existing_branch = cur.fetchone()
        
        if existing_branch:
            flash(f'يوجد فرع بالاسم "{name}" مسبقاً!', 'error')
            return redirect(url_for('branch.show_branches'))
        
        cur.execute('INSERT INTO Branch (name, address, phone) VALUES (?, ?, ?)',
                    (name, address if address else None, phone if phone else None))
        conn.commit()
        flash(f'تم إضافة الفرع "{name}" بنجاح!', 'success')
    except Exception as e:
        flash(f'خطأ في إضافة الفرع: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('branch.show_branches'))

@branch_bp.route('/update_branch/<int:id>', methods=['POST'])
def update_branch(id):
    name = request.form.get('name', '').strip()
    address = request.form.get('address', '').strip()
    phone = request.form.get('phone', '').strip()
    
    # التحقق من صحة البيانات
    if not name:
        flash('اسم الفرع مطلوب!', 'error')
        return redirect(url_for('branch.show_branches'))
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        # التحقق من عدم وجود فرع آخر بنفس الاسم
        cur.execute('SELECT name FROM Branch WHERE name = ? AND branch_id != ?', (name, id))
        existing_branch = cur.fetchone()
        
        if existing_branch:
            flash(f'يوجد فرع آخر بالاسم "{name}" مسبقاً!', 'error')
            return redirect(url_for('branch.show_branches'))
        
        cur.execute('UPDATE Branch SET name=?, address=?, phone=? WHERE branch_id=?',
                    (name, address if address else None, phone if phone else None, id))
        if cur.rowcount > 0:
            conn.commit()
            flash(f'تم تحديث الفرع "{name}" بنجاح!', 'success')
        else:
            flash('الفرع غير موجود!', 'error')
    except Exception as e:
        flash(f'خطأ في تحديث الفرع: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('branch.show_branches'))

@branch_bp.route('/delete_branch/<int:id>')
def delete_branch(id):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # جلب اسم الفرع أولاً
        cur.execute('SELECT name FROM Branch WHERE branch_id=?', (id,))
        branch = cur.fetchone()
        
        if branch:
            # التحقق من وجود كلاسات أو موظفين مرتبطين بهذا الفرع
            cur.execute('SELECT COUNT(*) FROM Class WHERE branch_id=?', (id,))
            classes_count = cur.fetchone()[0]
            
            cur.execute('SELECT COUNT(*) FROM Staff WHERE branch_id=?', (id,))
            staff_count = cur.fetchone()[0]
            
            if classes_count > 0 or staff_count > 0:
                flash(f'لا يمكن حذف الفرع "{branch[0]}" لأنه يحتوي على {classes_count} كلاس و {staff_count} موظف. يرجى نقلهم إلى فرع آخر أولاً.', 'error')
                return redirect(url_for('branch.show_branches'))
            
            cur.execute('DELETE FROM Branch WHERE branch_id=?', (id,))
            conn.commit()
            flash(f'تم حذف الفرع "{branch[0]}" بنجاح!', 'success')
        else:
            flash('الفرع غير موجود!', 'error')
    except Exception as e:
        flash(f'خطأ في حذف الفرع: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('branch.show_branches'))