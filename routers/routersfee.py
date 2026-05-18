from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Fee, Child

fee_bp = Blueprint('fee', __name__)


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


@fee_bp.route('/fees')
def show_fees():
    try:
        fees = Fee.query.order_by(Fee.due_date.desc(), Fee.created_at.desc()).all()
        children = Child.query.filter_by(is_active=True).order_by(Child.first_name.asc()).all()

        for fee in fees:
            fee.child_name = (
                f'{fee.child.first_name} {fee.child.last_name}'
                if fee.child else 'غير محدد'
            )

        for child in children:
            child.name = f'{child.first_name} {child.last_name}'

    except Exception as e:
        flash(f'خطأ في جلب البيانات: {str(e)}', 'error')
        fees = []
        children = []

    return render_template('fees.html', fees=fees, children=children)


@fee_bp.route('/add_fee', methods=['POST'])
def add_fee():
    child_id = request.form.get('child_id')
    amount = request.form.get('amount')
    due_date = request.form.get('due_date')
    status = request.form.get('status', 'Pending')
    payment_method = request.form.get('payment_method', '').strip()
    notes = request.form.get('notes', '').strip()

    if not child_id or not amount or not due_date:
        flash('جميع الحقول المطلوبة يجب ملؤها!', 'error')
        return redirect(url_for('fee.show_fees'))

    try:
        fee = Fee(
            child_id=int(child_id),
            amount=float(amount),
            due_date=parse_date(due_date),
            status=status,
            payment_method=payment_method or None,
            notes=notes or None
        )

        db.session.add(fee)
        db.session.commit()
        flash('تم إضافة الرسوم بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في إضافة الرسوم: {str(e)}', 'error')

    return redirect(url_for('fee.show_fees'))


@fee_bp.route('/update_fee/<int:id>', methods=['POST'])
def update_fee(id):
    fee = Fee.query.get(id)

    if not fee:
        flash('الرسوم غير موجودة!', 'error')
        return redirect(url_for('fee.show_fees'))

    child_id = request.form.get('child_id')
    amount = request.form.get('amount')
    due_date = request.form.get('due_date')
    status = request.form.get('status')
    paid_date = request.form.get('paid_date')
    payment_method = request.form.get('payment_method', '').strip()
    notes = request.form.get('notes', '').strip()

    if not child_id or not amount:
        flash('الحقول المطلوبة يجب ملؤها!', 'error')
        return redirect(url_for('fee.show_fees'))

    try:
        fee.child_id = int(child_id)
        fee.amount = float(amount)
        fee.due_date = parse_date(due_date)
        fee.status = status
        fee.paid_date = parse_date(paid_date)
        fee.payment_method = payment_method or None
        fee.notes = notes or None

        db.session.commit()
        flash('تم تحديث الرسوم بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في تحديث الرسوم: {str(e)}', 'error')

    return redirect(url_for('fee.show_fees'))


@fee_bp.route('/pay_fee/<int:id>', methods=['POST'])
def pay_fee(id):
    fee = Fee.query.get(id)

    if not fee:
        flash('الرسوم غير موجودة!', 'error')
        return redirect(url_for('fee.show_fees'))

    paid_date = request.form.get('paid_date')
    payment_method = request.form.get('payment_method', '').strip()
    notes = request.form.get('notes', '').strip()

    if not paid_date or not payment_method:
        flash('تاريخ الدفع وطريقة الدفع مطلوبان!', 'error')
        return redirect(url_for('fee.show_fees'))

    try:
        fee.status = 'Paid'
        fee.paid_date = parse_date(paid_date)
        fee.payment_method = payment_method
        fee.notes = notes or None

        db.session.commit()
        flash('تم تسجيل الدفع بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في تسجيل الدفع: {str(e)}', 'error')

    return redirect(url_for('fee.show_fees'))


@fee_bp.route('/process_payments', methods=['POST'])
def process_payments():
    fee_ids = request.form.getlist('fee_ids[]')
    payment_date = request.form.get('payment_date')
    payment_method = request.form.get('payment_method', '').strip()
    notes = request.form.get('notes', '').strip()

    if not fee_ids or not payment_date or not payment_method:
        flash('يجب اختيار رسوم للدفع وتحديد تاريخ وطريقة الدفع!', 'error')
        return redirect(url_for('fee.show_fees'))

    try:
        for fee_id in fee_ids:
            fee = Fee.query.get(int(fee_id))
            if fee:
                fee.status = 'Paid'
                fee.paid_date = parse_date(payment_date)
                fee.payment_method = payment_method
                fee.notes = notes or None

        db.session.commit()
        flash(f'تم تسجيل دفع {len(fee_ids)} رسوم بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في تسجيل الدفعات: {str(e)}', 'error')

    return redirect(url_for('fee.show_fees'))


@fee_bp.route('/delete_fee/<int:id>')
def delete_fee(id):
    fee = Fee.query.get(id)

    if not fee:
        flash('الرسوم غير موجودة!', 'error')
        return redirect(url_for('fee.show_fees'))

    child_name = (
        f'{fee.child.first_name} {fee.child.last_name}'
        if fee.child else 'الطفل'
    )
    amount = fee.amount

    try:
        db.session.delete(fee)
        db.session.commit()
        flash(f'تم حذف رسوم {child_name} بمبلغ {amount} جنيه بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في حذف الرسوم: {str(e)}', 'error')

    return redirect(url_for('fee.show_fees'))