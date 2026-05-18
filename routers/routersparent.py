from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_conn

parent_bp = Blueprint('parent', __name__)

@parent_bp.route('/parents')
def show_parents():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM Parent ORDER BY created_at DESC')
        parents = cur.fetchall()
    except Exception as e:
        print(f"خطأ في قاعدة البيانات: {e}")
        flash(f'خطأ في جلب البيانات: {str(e)}', 'error')
        parents = []
    finally:
        conn.close()
    
    return render_template('parent.html', parents=parents)

@parent_bp.route('/add_parent', methods=['POST'])
def add_parent():
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()
    
    print(f"=== DEBUG: إضافة ولي أمر ===")
    print(f"البيانات: {first_name}, {last_name}, {phone}, {email}")
    
    # التحقق من صحة البيانات
    if not first_name or not last_name:
        flash('الاسم الأول والأخير مطلوبان!', 'error')
        return redirect(url_for('parent.show_parents'))
    
    # تحويل القيم الفارغة إلى None
    phone = phone if phone else None
    email = email if email else None
    address = address if address else None
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO Parent (first_name, last_name, phone, email, address) 
            VALUES (?, ?, ?, ?, ?)
        ''', (first_name, last_name, phone, email, address))
        conn.commit()
        print(f"✅ تم إضافة ولي الأمر بنجاح: {first_name} {last_name}")
        flash(f'تم إضافة ولي الأمر "{first_name} {last_name}" بنجاح!', 'success')
    except Exception as e:
        print(f"❌ خطأ في إضافة ولي الأمر: {e}")
        flash(f'خطأ في إضافة ولي الأمر: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('parent.show_parents'))

@parent_bp.route('/update_parent/<int:id>', methods=['POST'])
def update_parent(id):
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()
    
    # التحقق من صحة البيانات
    if not first_name or not last_name:
        flash('الاسم الأول والأخير مطلوبان!', 'error')
        return redirect(url_for('parent.show_parents'))
    
    # تحويل القيم الفارغة إلى None
    phone = phone if phone else None
    email = email if email else None
    address = address if address else None
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''
            UPDATE Parent 
            SET first_name=?, last_name=?, phone=?, email=?, address=? 
            WHERE parent_id=?
        ''', (first_name, last_name, phone, email, address, id))
        
        if cur.rowcount > 0:
            conn.commit()
            flash(f'تم تحديث ولي الأمر "{first_name} {last_name}" بنجاح!', 'success')
        else:
            flash('ولي الأمر غير موجود!', 'error')
    except Exception as e:
        flash(f'خطأ في تحديث ولي الأمر: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('parent.show_parents'))

@parent_bp.route('/delete_parent/<int:id>')
def delete_parent(id):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # جلب اسم ولي الأمر أولاً
        cur.execute('SELECT first_name, last_name FROM Parent WHERE parent_id=?', (id,))
        parent = cur.fetchone()
        
        if parent:
            cur.execute('DELETE FROM Parent WHERE parent_id=?', (id,))
            conn.commit()
            flash(f'تم حذف ولي الأمر "{parent[0]} {parent[1]}" بنجاح!', 'success')
        else:
            flash('ولي الأمر غير موجود!', 'error')
    except Exception as e:
        flash(f'خطأ في حذف ولي الأمر: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('parent.show_parents'))