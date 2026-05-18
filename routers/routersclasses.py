from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Class, Branch

classes_bp = Blueprint('classes', __name__)


@classes_bp.route('/classes')
def show_classes():
    try:
        classes = Class.query.order_by(Class.created_at.desc()).all()
        branches = Branch.query.order_by(Branch.name.asc()).all()

        for classroom in classes:
            classroom.branch_name = classroom.branch.name if classroom.branch else None

    except Exception as e:
        flash(f'خطأ في جلب البيانات: {str(e)}', 'error')
        classes = []
        branches = []

    return render_template('class.html', classes=classes, branches=branches)


@classes_bp.route('/add_class', methods=['POST'])
def add_class():
    name = request.form.get('name', '').strip()
    branch_id = request.form.get('branch_id')
    max_capacity = request.form.get('max_capacity', '25')
    age_group = request.form.get('age_group', '').strip()

    if not name:
        flash('اسم الكلاس مطلوب!', 'error')
        return redirect(url_for('classes.show_classes'))

    try:
        branch_id = int(branch_id) if branch_id else None
        max_capacity = int(max_capacity) if max_capacity else 25
    except ValueError:
        flash('بيانات غير صحيحة في الفرع أو السعة.', 'error')
        return redirect(url_for('classes.show_classes'))

    classroom = Class(
        name=name,
        branch_id=branch_id,
        max_capacity=max_capacity,
        age_group=age_group or None
    )

    try:
        db.session.add(classroom)
        db.session.commit()
        flash(f'تم إضافة الكلاس "{name}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في إضافة الكلاس: {str(e)}', 'error')

    return redirect(url_for('classes.show_classes'))


@classes_bp.route('/update_class/<int:id>', methods=['POST'])
def update_class(id):
    classroom = Class.query.get(id)

    if not classroom:
        flash('الكلاس غير موجود!', 'error')
        return redirect(url_for('classes.show_classes'))

    name = request.form.get('name', '').strip()
    branch_id = request.form.get('branch_id')
    max_capacity = request.form.get('max_capacity', '25')
    age_group = request.form.get('age_group', '').strip()

    if not name:
        flash('اسم الكلاس مطلوب!', 'error')
        return redirect(url_for('classes.show_classes'))

    try:
        classroom.name = name
        classroom.branch_id = int(branch_id) if branch_id else None
        classroom.max_capacity = int(max_capacity) if max_capacity else 25
        classroom.age_group = age_group or None

        db.session.commit()
        flash(f'تم تحديث الكلاس "{name}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في تحديث الكلاس: {str(e)}', 'error')

    return redirect(url_for('classes.show_classes'))


@classes_bp.route('/delete_class/<int:id>')
def delete_class(id):
    classroom = Class.query.get(id)

    if not classroom:
        flash('الكلاس غير موجود!', 'error')
        return redirect(url_for('classes.show_classes'))

    if classroom.children:
        flash(f'لا يمكن حذف الكلاس "{classroom.name}" لأنه يحتوي على أطفال. انقلي الأطفال لكلاس آخر أولاً.', 'error')
        return redirect(url_for('classes.show_classes'))

    class_name = classroom.name

    try:
        db.session.delete(classroom)
        db.session.commit()
        flash(f'تم حذف الكلاس "{class_name}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في حذف الكلاس: {str(e)}', 'error')

    return redirect(url_for('classes.show_classes'))