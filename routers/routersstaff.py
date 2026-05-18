from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Staff, Branch

staff_bp = Blueprint('staff', __name__)


@staff_bp.route('/staff')
def show_staff():
    try:
        staff = Staff.query.order_by(Staff.created_at.desc()).all()
        branches = Branch.query.order_by(Branch.name.asc()).all()

        for staff_member in staff:
            staff_member.branch_name = staff_member.branch.name if staff_member.branch else 'غير محدد'

    except Exception as e:
        flash(f'خطأ في جلب البيانات: {str(e)}', 'error')
        staff = []
        branches = []

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

    if not first_name or not last_name:
        flash('الاسم الأول والأخير مطلوبان!', 'error')
        return redirect(url_for('staff.show_staff'))

    if not position:
        flash('المنصب مطلوب!', 'error')
        return redirect(url_for('staff.show_staff'))

    try:
        staff_member = Staff(
            first_name=first_name,
            last_name=last_name,
            phone=phone or None,
            email=email or None,
            position=position,
            branch_id=int(branch_id) if branch_id else None,
            salary=float(salary) if salary else None,
            is_active=True
        )

        db.session.add(staff_member)
        db.session.commit()
        flash(f'تم إضافة الموظف "{first_name} {last_name}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في إضافة الموظف: {str(e)}', 'error')

    return redirect(url_for('staff.show_staff'))


@staff_bp.route('/update_staff/<int:id>', methods=['POST'])
def update_staff(id):
    staff_member = Staff.query.get(id)

    if not staff_member:
        flash('الموظف غير موجود!', 'error')
        return redirect(url_for('staff.show_staff'))

    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    position = request.form.get('position', '').strip()
    branch_id = request.form.get('branch_id')
    salary = request.form.get('salary', '').strip()

    if not first_name or not last_name:
        flash('الاسم الأول والأخير مطلوبان!', 'error')
        return redirect(url_for('staff.show_staff'))

    if not position:
        flash('المنصب مطلوب!', 'error')
        return redirect(url_for('staff.show_staff'))

    try:
        staff_member.first_name = first_name
        staff_member.last_name = last_name
        staff_member.phone = phone or None
        staff_member.email = email or None
        staff_member.position = position
        staff_member.branch_id = int(branch_id) if branch_id else None
        staff_member.salary = float(salary) if salary else None

        db.session.commit()
        flash(f'تم تحديث الموظف "{first_name} {last_name}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في تحديث الموظف: {str(e)}', 'error')

    return redirect(url_for('staff.show_staff'))


@staff_bp.route('/delete_staff/<int:id>')
def delete_staff(id):
    staff_member = Staff.query.get(id)

    if not staff_member:
        flash('الموظف غير موجود!', 'error')
        return redirect(url_for('staff.show_staff'))

    full_name = f'{staff_member.first_name} {staff_member.last_name}'

    try:
        db.session.delete(staff_member)
        db.session.commit()
        flash(f'تم حذف الموظف "{full_name}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في حذف الموظف: {str(e)}', 'error')

    return redirect(url_for('staff.show_staff'))