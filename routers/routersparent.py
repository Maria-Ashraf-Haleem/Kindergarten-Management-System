from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Parent

parent_bp = Blueprint('parent', __name__)


@parent_bp.route('/parents')
def show_parents():
    try:
        parents = Parent.query.order_by(Parent.created_at.desc()).all()
    except Exception as e:
        flash(f'خطأ في جلب البيانات: {str(e)}', 'error')
        parents = []

    return render_template('parent.html', parents=parents)


@parent_bp.route('/add_parent', methods=['POST'])
def add_parent():
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()

    if not first_name or not last_name:
        flash('الاسم الأول والأخير مطلوبان!', 'error')
        return redirect(url_for('parent.show_parents'))

    parent = Parent(
        first_name=first_name,
        last_name=last_name,
        phone=phone or None,
        email=email or None,
        address=address or None
    )

    try:
        db.session.add(parent)
        db.session.commit()
        flash(f'تم إضافة ولي الأمر "{first_name} {last_name}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في إضافة ولي الأمر: {str(e)}', 'error')

    return redirect(url_for('parent.show_parents'))


@parent_bp.route('/update_parent/<int:id>', methods=['POST'])
def update_parent(id):
    parent = Parent.query.get(id)

    if not parent:
        flash('ولي الأمر غير موجود!', 'error')
        return redirect(url_for('parent.show_parents'))

    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()

    if not first_name or not last_name:
        flash('الاسم الأول والأخير مطلوبان!', 'error')
        return redirect(url_for('parent.show_parents'))

    parent.first_name = first_name
    parent.last_name = last_name
    parent.phone = phone or None
    parent.email = email or None
    parent.address = address or None

    try:
        db.session.commit()
        flash(f'تم تحديث ولي الأمر "{first_name} {last_name}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في تحديث ولي الأمر: {str(e)}', 'error')

    return redirect(url_for('parent.show_parents'))


@parent_bp.route('/delete_parent/<int:id>')
def delete_parent(id):
    parent = Parent.query.get(id)

    if not parent:
        flash('ولي الأمر غير موجود!', 'error')
        return redirect(url_for('parent.show_parents'))

    if parent.children:
        flash('لا يمكن حذف ولي الأمر لأنه مرتبط بأطفال. احذفي الأطفال المرتبطين به أولاً أو انقليهم لولي أمر آخر.', 'error')
        return redirect(url_for('parent.show_parents'))

    full_name = f'{parent.first_name} {parent.last_name}'

    try:
        db.session.delete(parent)
        db.session.commit()
        flash(f'تم حذف ولي الأمر "{full_name}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في حذف ولي الأمر: {str(e)}', 'error')

    return redirect(url_for('parent.show_parents'))