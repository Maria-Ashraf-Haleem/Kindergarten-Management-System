from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Branch

branch_bp = Blueprint('branch', __name__)


@branch_bp.route('/branches')
def show_branches():
    try:
        branches = Branch.query.order_by(Branch.created_at.desc()).all()

        for branch in branches:
            branch.classes_count = len(branch.classes)
            branch.staff_count = len(branch.staff_members)

    except Exception as e:
        flash(f'خطأ في جلب البيانات: {str(e)}', 'error')
        branches = []

    return render_template('branch.html', branches=branches)


@branch_bp.route('/add_branch', methods=['POST'])
def add_branch():
    name = request.form.get('name', '').strip()
    address = request.form.get('address', '').strip()
    phone = request.form.get('phone', '').strip()

    if not name:
        flash('اسم الفرع مطلوب!', 'error')
        return redirect(url_for('branch.show_branches'))

    existing_branch = Branch.query.filter_by(name=name).first()
    if existing_branch:
        flash(f'يوجد فرع بالاسم "{name}" مسبقاً!', 'error')
        return redirect(url_for('branch.show_branches'))

    branch = Branch(
        name=name,
        address=address or None,
        phone=phone or None
    )

    try:
        db.session.add(branch)
        db.session.commit()
        flash(f'تم إضافة الفرع "{name}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في إضافة الفرع: {str(e)}', 'error')

    return redirect(url_for('branch.show_branches'))


@branch_bp.route('/update_branch/<int:id>', methods=['POST'])
def update_branch(id):
    branch = Branch.query.get(id)

    if not branch:
        flash('الفرع غير موجود!', 'error')
        return redirect(url_for('branch.show_branches'))

    name = request.form.get('name', '').strip()
    address = request.form.get('address', '').strip()
    phone = request.form.get('phone', '').strip()

    if not name:
        flash('اسم الفرع مطلوب!', 'error')
        return redirect(url_for('branch.show_branches'))

    existing_branch = Branch.query.filter(
        Branch.name == name,
        Branch.branch_id != id
    ).first()

    if existing_branch:
        flash(f'يوجد فرع آخر بالاسم "{name}" مسبقاً!', 'error')
        return redirect(url_for('branch.show_branches'))

    branch.name = name
    branch.address = address or None
    branch.phone = phone or None

    try:
        db.session.commit()
        flash(f'تم تحديث الفرع "{name}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في تحديث الفرع: {str(e)}', 'error')

    return redirect(url_for('branch.show_branches'))


@branch_bp.route('/delete_branch/<int:id>')
def delete_branch(id):
    branch = Branch.query.get(id)

    if not branch:
        flash('الفرع غير موجود!', 'error')
        return redirect(url_for('branch.show_branches'))

    classes_count = len(branch.classes)
    staff_count = len(branch.staff_members)

    if classes_count > 0 or staff_count > 0:
        flash(
            f'لا يمكن حذف الفرع "{branch.name}" لأنه يحتوي على {classes_count} كلاس و {staff_count} موظف. يرجى نقلهم إلى فرع آخر أولاً.',
            'error'
        )
        return redirect(url_for('branch.show_branches'))

    branch_name = branch.name

    try:
        db.session.delete(branch)
        db.session.commit()
        flash(f'تم حذف الفرع "{branch_name}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في حذف الفرع: {str(e)}', 'error')

    return redirect(url_for('branch.show_branches'))