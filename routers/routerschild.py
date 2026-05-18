from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_conn, log_activity

child_bp = Blueprint('child', __name__)

@child_bp.route('/children')
def show_children():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''
            SELECT c.*, 
                   CASE WHEN p.first_name IS NOT NULL 
                        THEN p.first_name || " " || p.last_name 
                        ELSE 'غير محدد' 
                   END as parent_name, 
                   CASE WHEN cl.name IS NOT NULL 
                        THEN cl.name 
                        ELSE 'غير محدد' 
                   END as class_name,
                   CASE WHEN b.name IS NOT NULL 
                        THEN b.name 
                        ELSE 'غير محدد' 
                   END as branch_name
            FROM Child c
            LEFT JOIN Parent p ON c.parent_id = p.parent_id
            LEFT JOIN Class cl ON c.class_id = cl.class_id
            LEFT JOIN Branch b ON cl.branch_id = b.branch_id
            WHERE c.is_active = 1
            ORDER BY c.created_at DESC
        ''')
        children = cur.fetchall()
        
        # جلب الأولياء للاختيار
        cur.execute('SELECT parent_id, first_name || " " || last_name as name FROM Parent ORDER BY first_name')
        parents = cur.fetchall()
        
        # جلب الكلاسات للاختيار
        cur.execute('''
            SELECT cl.class_id, cl.name, b.name as branch_name
            FROM Class cl
            LEFT JOIN Branch b ON cl.branch_id = b.branch_id
            ORDER BY cl.name
        ''')
        classes = cur.fetchall()
        
    except Exception as e:
        print(f"خطأ في قاعدة البيانات: {e}")
        flash(f'خطأ في جلب البيانات: {str(e)}', 'error')
        children = []
        parents = []
        classes = []
    finally:
        conn.close()
    
    return render_template('child.html', children=children, parents=parents, classes=classes)

@child_bp.route('/add_child', methods=['POST'])
def add_child():
    print("=== DEBUG: دخل دالة add_child ===")
    print(f"Form data: {request.form}")
    
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    date_of_birth = request.form.get('date_of_birth', '').strip()
    gender = request.form.get('gender', 'Male')
    parent_id = request.form.get('parent_id')
    class_id = request.form.get('class_id')
    
    print(f"البيانات المستلمة: {first_name}, {last_name}, {date_of_birth}, {gender}, {parent_id}, {class_id}")
    
    # التحقق من صحة البيانات الأساسية
    if not first_name or not last_name:
        flash('الاسم الأول والأخير مطلوبان!', 'error')
        return redirect(url_for('child.show_children'))
    
    # تحويل القيم الفارغة إلى None
    parent_id = int(parent_id) if parent_id and parent_id != '' else None
    class_id = int(class_id) if class_id and class_id != '' else None
    date_of_birth = date_of_birth if date_of_birth else None
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO Child (first_name, last_name, date_of_birth, gender, parent_id, class_id, is_active) 
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (first_name, last_name, date_of_birth, gender, parent_id, class_id))
        conn.commit()
        print(f"✅ تم إضافة الطفل بنجاح: {first_name} {last_name}")
        flash(f'تم إضافة الطفل "{first_name} {last_name}" بنجاح!', 'success')
        
        # تسجيل النشاط
        log_activity('new_child', f'تم تسجيل طفل جديد: {first_name} {last_name}')
    except Exception as e:
        print(f"❌ خطأ في إضافة الطفل: {e}")
        flash(f'خطأ في إضافة الطفل: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('child.show_children'))

@child_bp.route('/update_child/<int:id>', methods=['POST'])
def update_child(id):
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    date_of_birth = request.form.get('date_of_birth', '').strip()
    gender = request.form.get('gender', 'Male')
    parent_id = request.form.get('parent_id')
    class_id = request.form.get('class_id')
    
    # التحقق من صحة البيانات
    if not first_name or not last_name:
        flash('الاسم الأول والأخير مطلوبان!', 'error')
        return redirect(url_for('child.show_children'))
    
    # تحويل القيم الفارغة إلى None
    parent_id = int(parent_id) if parent_id and parent_id != '' else None
    class_id = int(class_id) if class_id and class_id != '' else None
    date_of_birth = date_of_birth if date_of_birth else None
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''
            UPDATE Child 
            SET first_name=?, last_name=?, date_of_birth=?, gender=?, parent_id=?, class_id=? 
            WHERE child_id=?
        ''', (first_name, last_name, date_of_birth, gender, parent_id, class_id, id))
        
        if cur.rowcount > 0:
            conn.commit()
            flash(f'تم تحديث الطفل "{first_name} {last_name}" بنجاح!', 'success')
        else:
            flash('الطفل غير موجود!', 'error')
    except Exception as e:
        flash(f'خطأ في تحديث الطفل: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('child.show_children'))

@child_bp.route('/delete_child/<int:id>')
def delete_child(id):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # جلب اسم الطفل أولاً
        cur.execute('SELECT first_name, last_name FROM Child WHERE child_id=?', (id,))
        child = cur.fetchone()
        
        if child:
            # حذف منطقي بدلاً من حذف فعلي
            cur.execute('UPDATE Child SET is_active = 0 WHERE child_id=?', (id,))
            conn.commit()
            flash(f'تم حذف الطفل "{child[0]} {child[1]}" بنجاح!', 'success')
        else:
            flash('الطفل غير موجود!', 'error')
    except Exception as e:
        flash(f'خطأ في حذف الطفل: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('child.show_children'))