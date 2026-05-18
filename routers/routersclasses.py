from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_conn

classes_bp = Blueprint('classes', __name__)

@classes_bp.route('/classes')
def show_classes():
    conn = get_conn()
    cur = conn.cursor()
    try:
        # جلب الكلاسات مع معلومات الفرع
        cur.execute('''
            SELECT cl.*, b.name as branch_name
            FROM Class cl
            LEFT JOIN Branch b ON cl.branch_id = b.branch_id
            ORDER BY cl.created_at DESC
        ''')
        classes = cur.fetchall()
        
        # جلب الفروع للاختيار
        cur.execute('SELECT branch_id, name FROM Branch ORDER BY name')
        branches = cur.fetchall()
        
    except Exception as e:
        flash(f'خطأ في جلب البيانات: {str(e)}', 'error')
        classes = []
        branches = []
    finally:
        conn.close()
    
    return render_template('class.html', classes=classes, branches=branches)

@classes_bp.route('/add_class', methods=['POST'])
def add_class():
    name = request.form.get('name', '').strip()
    branch_id = request.form.get('branch_id')
    max_capacity = request.form.get('max_capacity', '25')
    age_group = request.form.get('age_group', '').strip()
    
    # التحقق من صحة البيانات
    if not name:
        flash('اسم الكلاس مطلوب!', 'error')
        return redirect(url_for('classes.show_classes'))
    
    # تحويل القيم
    branch_id = int(branch_id) if branch_id and branch_id != '' else None
    max_capacity = int(max_capacity) if max_capacity else 25
    age_group = age_group if age_group else None
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO Class (name, branch_id, max_capacity, age_group) 
            VALUES (?, ?, ?, ?)
        ''', (name, branch_id, max_capacity, age_group))
        conn.commit()
        flash(f'تم إضافة الكلاس "{name}" بنجاح!', 'success')
    except Exception as e:
        flash(f'خطأ في إضافة الكلاس: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('classes.show_classes'))

@classes_bp.route('/update_class/<int:id>', methods=['POST'])
def update_class(id):
    name = request.form.get('name', '').strip()
    branch_id = request.form.get('branch_id')
    max_capacity = request.form.get('max_capacity', '25')
    age_group = request.form.get('age_group', '').strip()
    
    # التحقق من صحة البيانات
    if not name:
        flash('اسم الكلاس مطلوب!', 'error')
        return redirect(url_for('classes.show_classes'))
    
    # تحويل القيم
    branch_id = int(branch_id) if branch_id and branch_id != '' else None
    max_capacity = int(max_capacity) if max_capacity else 25
    age_group = age_group if age_group else None
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''
            UPDATE Class 
            SET name=?, branch_id=?, max_capacity=?, age_group=? 
            WHERE class_id=?
        ''', (name, branch_id, max_capacity, age_group, id))
        
        if cur.rowcount > 0:
            conn.commit()
            flash(f'تم تحديث الكلاس "{name}" بنجاح!', 'success')
        else:
            flash('الكلاس غير موجود!', 'error')
    except Exception as e:
        flash(f'خطأ في تحديث الكلاس: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('classes.show_classes'))

@classes_bp.route('/delete_class/<int:id>')
def delete_class(id):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # جلب اسم الكلاس أولاً
        cur.execute('SELECT name FROM Class WHERE class_id=?', (id,))
        class_info = cur.fetchone()
        
        if class_info:
            cur.execute('DELETE FROM Class WHERE class_id=?', (id,))
            conn.commit()
            flash(f'تم حذف الكلاس "{class_info[0]}" بنجاح!', 'success')
        else:
            flash('الكلاس غير موجود!', 'error')
    except Exception as e:
        flash(f'خطأ في حذف الكلاس: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('classes.show_classes'))