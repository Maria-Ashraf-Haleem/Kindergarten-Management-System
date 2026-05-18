from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_conn, log_activity

fee_bp = Blueprint('fee', __name__)

@fee_bp.route('/fees')
def show_fees():
    conn = get_conn()
    cur = conn.cursor()
    try:
        # جلب الرسوم مع أسماء الأطفال
        cur.execute('''
            SELECT f.*, c.first_name || " " || c.last_name as child_name
            FROM Fee f
            LEFT JOIN Child c ON f.child_id = c.child_id
            ORDER BY f.due_date DESC, f.created_at DESC
        ''')
        fees = cur.fetchall()
        
        # جلب الأطفال للاختيار
        cur.execute('SELECT child_id, first_name || " " || last_name as name FROM Child WHERE is_active = 1')
        children = cur.fetchall()
        
    except Exception as e:
        flash(f'خطأ في جلب البيانات: {str(e)}', 'error')
        fees = []
        children = []
    finally:
        conn.close()
    
    return render_template('fees.html', fees=fees, children=children)

@fee_bp.route('/add_fee', methods=['POST'])
def add_fee():
    child_id = request.form.get('child_id')
    amount = request.form.get('amount')
    due_date = request.form.get('due_date')
    status = request.form.get('status', 'Pending')
    payment_method = request.form.get('payment_method', '')
    notes = request.form.get('notes', '')
    
    if not child_id or not amount or not due_date:
        flash('جميع الحقول المطلوبة يجب ملؤها!', 'error')
        return redirect(url_for('fee.show_fees'))
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''INSERT INTO Fee (child_id, amount, due_date, status, payment_method, notes) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (child_id, float(amount), due_date, status, payment_method if payment_method else None, notes))
        conn.commit()
        flash('تم إضافة الرسوم بنجاح!', 'success')
    except Exception as e:
        flash(f'خطأ في إضافة الرسوم: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('fee.show_fees'))

@fee_bp.route('/update_fee/<int:id>', methods=['POST'])
def update_fee(id):
    child_id = request.form.get('child_id')
    amount = request.form.get('amount')
    due_date = request.form.get('due_date')
    status = request.form.get('status')
    paid_date = request.form.get('paid_date')
    payment_method = request.form.get('payment_method')
    notes = request.form.get('notes', '')
    
    if not child_id or not amount:
        flash('الحقول المطلوبة يجب ملؤها!', 'error')
        return redirect(url_for('fee.show_fees'))
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''UPDATE Fee 
                       SET child_id=?, amount=?, due_date=?, status=?, paid_date=?, 
                           payment_method=?, notes=?
                       WHERE fee_id=?''',
                    (child_id, float(amount), due_date, status, 
                     paid_date if paid_date else None,
                     payment_method if payment_method else None, 
                     notes, id))
        
        if cur.rowcount > 0:
            conn.commit()
            flash('تم تحديث الرسوم بنجاح!', 'success')
        else:
            flash('الرسوم غير موجودة!', 'error')
    except Exception as e:
        flash(f'خطأ في تحديث الرسوم: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('fee.show_fees'))

@fee_bp.route('/pay_fee/<int:id>', methods=['POST'])
def pay_fee(id):
    paid_date = request.form.get('paid_date')
    payment_method = request.form.get('payment_method')
    notes = request.form.get('notes', '')
    
    if not paid_date or not payment_method:
        flash('تاريخ الدفع وطريقة الدفع مطلوبان!', 'error')
        return redirect(url_for('fee.show_fees'))
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''UPDATE Fee 
                       SET status='Paid', paid_date=?, payment_method=?, notes=?
                       WHERE fee_id=?''',
                    (paid_date, payment_method, notes, id))
        
        if cur.rowcount > 0:
            # جلب اسم الطفل قبل الـ commit
            cur.execute('''SELECT c.first_name || " " || c.last_name as child_name
                          FROM Fee f
                          LEFT JOIN Child c ON f.child_id = c.child_id
                          WHERE f.fee_id = ?''', (id,))
            child_info = cur.fetchone()
            child_name = child_info[0] if child_info else "الطفل"
            
            conn.commit()
            flash('تم تسجيل الدفع بنجاح!', 'success')
            
            # تسجيل النشاط
            log_activity('payment', f'تم دفع رسوم لـ {child_name}')
        else:
            flash('الرسوم غير موجودة!', 'error')
    except Exception as e:
        flash(f'خطأ في تسجيل الدفع: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('fee.show_fees'))

@fee_bp.route('/process_payments', methods=['POST'])
def process_payments():
    fee_ids = request.form.getlist('fee_ids[]')
    payment_date = request.form.get('payment_date')
    payment_method = request.form.get('payment_method')
    notes = request.form.get('notes', '')
    
    if not fee_ids or not payment_date or not payment_method:
        flash('يجب اختيار رسوم للدفع وتحديد تاريخ وطريقة الدفع!', 'error')
        return redirect(url_for('fee.show_fees'))
    
    conn = get_conn()
    cur = conn.cursor()
    try:
        for fee_id in fee_ids:
            cur.execute('''UPDATE Fee 
                           SET status='Paid', paid_date=?, payment_method=?, notes=?
                           WHERE fee_id=?''',
                        (payment_date, payment_method, notes, fee_id))
        
        conn.commit()
        flash(f'تم تسجيل دفع {len(fee_ids)} رسوم بنجاح!', 'success')
        
        # تسجيل النشاط
        log_activity('payment', f'تم دفع {len(fee_ids)} رسوم')
    except Exception as e:
        flash(f'خطأ في تسجيل الدفعات: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('fee.show_fees'))

@fee_bp.route('/delete_fee/<int:id>')
def delete_fee(id):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # جلب معلومات الرسوم أولاً
        cur.execute('''SELECT f.amount, c.first_name || " " || c.last_name as child_name
                       FROM Fee f 
                       LEFT JOIN Child c ON f.child_id = c.child_id 
                       WHERE f.fee_id=?''', (id,))
        fee_info = cur.fetchone()
        
        if fee_info:
            cur.execute('DELETE FROM Fee WHERE fee_id=?', (id,))
            conn.commit()
            flash(f'تم حذف رسوم {fee_info[1]} بمبلغ {fee_info[0]} جنيه بنجاح!', 'success')
        else:
            flash('الرسوم غير موجودة!', 'error')
    except Exception as e:
        flash(f'خطأ في حذف الرسوم: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('fee.show_fees'))