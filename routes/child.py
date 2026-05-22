from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models import Child, Parent, Class

child_bp = Blueprint('child', __name__)


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


@child_bp.route('/children')
def show_children():
    user_id = session['user_id']

    try:
        children = Child.query.filter_by(
            is_active=True,
            user_id=user_id
        ).order_by(Child.created_at.desc()).all()

        parents = Parent.query.filter_by(user_id=user_id).order_by(
            Parent.first_name.asc(),
            Parent.last_name.asc()
        ).all()

        classes = Class.query.filter_by(user_id=user_id).order_by(Class.name.asc()).all()

        for child in children:
            child.parent_name = (
                f'{child.parent.first_name} {child.parent.last_name}'
                if child.parent else 'غير محدد'
            )
            child.class_name = child.classroom.name if child.classroom else 'غير محدد'
            child.branch_name = (
                child.classroom.branch.name
                if child.classroom and child.classroom.branch else 'غير محدد'
            )

        for parent in parents:
            parent.name = f'{parent.first_name} {parent.last_name}'

        for classroom in classes:
            classroom.branch_name = classroom.branch.name if classroom.branch else 'غير محدد'

    except Exception as e:
        flash(f'خطأ في جلب البيانات: {str(e)}', 'error')
        children = []
        parents = []
        classes = []

    return render_template('child.html', children=children, parents=parents, classes=classes)


@child_bp.route('/add_child', methods=['POST'])
def add_child():
    user_id = session['user_id']

    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    date_of_birth = request.form.get('date_of_birth', '').strip()
    gender = request.form.get('gender', 'Male')
    parent_id = request.form.get('parent_id')
    class_id = request.form.get('class_id')

    if not first_name or not last_name:
        flash('الاسم الأول والأخير مطلوبان!', 'error')
        return redirect(url_for('child.show_children'))

    try:
        parent_id = int(parent_id) if parent_id else None
        class_id = int(class_id) if class_id else None
    except ValueError:
        flash('بيانات ولي الأمر أو الكلاس غير صحيحة.', 'error')
        return redirect(url_for('child.show_children'))

    if parent_id:
        parent = Parent.query.filter_by(parent_id=parent_id, user_id=user_id).first()
        if not parent:
            flash('ولي الأمر غير موجود أو لا يخص هذا المستخدم.', 'error')
            return redirect(url_for('child.show_children'))

    if class_id:
        classroom = Class.query.filter_by(class_id=class_id, user_id=user_id).first()
        if not classroom:
            flash('الكلاس غير موجود أو لا يخص هذا المستخدم.', 'error')
            return redirect(url_for('child.show_children'))

    child = Child(
        first_name=first_name,
        last_name=last_name,
        date_of_birth=parse_date(date_of_birth),
        gender=gender,
        parent_id=parent_id,
        class_id=class_id,
        is_active=True,
        user_id=user_id
    )

    try:
        db.session.add(child)
        db.session.commit()
        flash(f'تم إضافة الطفل "{first_name} {last_name}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في إضافة الطفل: {str(e)}', 'error')

    return redirect(url_for('child.show_children'))


@child_bp.route('/update_child/<int:id>', methods=['POST'])
def update_child(id):
    user_id = session['user_id']

    child = Child.query.filter_by(child_id=id, user_id=user_id).first()

    if not child:
        flash('الطفل غير موجود!', 'error')
        return redirect(url_for('child.show_children'))

    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    date_of_birth = request.form.get('date_of_birth', '').strip()
    gender = request.form.get('gender', 'Male')
    parent_id = request.form.get('parent_id')
    class_id = request.form.get('class_id')

    if not first_name or not last_name:
        flash('الاسم الأول والأخير مطلوبان!', 'error')
        return redirect(url_for('child.show_children'))

    try:
        parent_id = int(parent_id) if parent_id else None
        class_id = int(class_id) if class_id else None
    except ValueError:
        flash('بيانات ولي الأمر أو الكلاس غير صحيحة.', 'error')
        return redirect(url_for('child.show_children'))

    if parent_id:
        parent = Parent.query.filter_by(parent_id=parent_id, user_id=user_id).first()
        if not parent:
            flash('ولي الأمر غير موجود أو لا يخص هذا المستخدم.', 'error')
            return redirect(url_for('child.show_children'))

    if class_id:
        classroom = Class.query.filter_by(class_id=class_id, user_id=user_id).first()
        if not classroom:
            flash('الكلاس غير موجود أو لا يخص هذا المستخدم.', 'error')
            return redirect(url_for('child.show_children'))

    child.first_name = first_name
    child.last_name = last_name
    child.date_of_birth = parse_date(date_of_birth)
    child.gender = gender
    child.parent_id = parent_id
    child.class_id = class_id

    try:
        db.session.commit()
        flash(f'تم تحديث الطفل "{first_name} {last_name}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في تحديث الطفل: {str(e)}', 'error')

    return redirect(url_for('child.show_children'))


@child_bp.route('/delete_child/<int:id>')
def delete_child(id):
    user_id = session['user_id']

    child = Child.query.filter_by(child_id=id, user_id=user_id).first()

    if not child:
        flash('الطفل غير موجود!', 'error')
        return redirect(url_for('child.show_children'))

    full_name = f'{child.first_name} {child.last_name}'

    try:
        child.is_active = False
        db.session.commit()
        flash(f'تم حذف الطفل "{full_name}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في حذف الطفل: {str(e)}', 'error')

    return redirect(url_for('child.show_children'))