from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models import Attendance, Child, Class

attendance_bp = Blueprint('attendance', __name__)


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def parse_time(value):
    if not value:
        return None

    try:
        return datetime.strptime(value, '%H:%M').time()
    except ValueError:
        return None


@attendance_bp.route('/attendance')
def show_attendance():
    user_id = session['user_id']

    try:
        attendance_records = Attendance.query.filter_by(user_id=user_id).order_by(
            Attendance.date.desc(),
            Attendance.created_at.desc()
        ).limit(100).all()

        children = Child.query.filter_by(user_id=user_id, is_active=True).order_by(
            Child.first_name.asc(),
            Child.last_name.asc()
        ).all()

        for record in attendance_records:
            record.child_name = (
                f'{record.child.first_name} {record.child.last_name}'
                if record.child else 'غير محدد'
            )
            record.class_name = (
                record.child.classroom.name
                if record.child and record.child.classroom else 'غير محدد'
            )
            record.branch_name = (
                record.child.classroom.branch.name
                if record.child and record.child.classroom and record.child.classroom.branch else 'غير محدد'
            )

        for child in children:
            child.name = f'{child.first_name} {child.last_name}'
            child.class_name = child.classroom.name if child.classroom else 'غير محدد'

    except Exception as e:
        flash(f'خطأ في جلب البيانات: {str(e)}', 'error')
        attendance_records = []
        children = []

    return render_template(
        'attendance.html',
        attendance_records=attendance_records,
        children=children
    )


@attendance_bp.route('/add_attendance', methods=['POST'])
def add_attendance():
    user_id = session['user_id']

    child_id = request.form.get('child_id')
    date_str = request.form.get('date')
    status = request.form.get('status')
    check_in_time = request.form.get('check_in_time', '').strip()
    check_out_time = request.form.get('check_out_time', '').strip()
    notes = request.form.get('notes', '').strip()

    if not child_id or not date_str or not status:
        flash('الطفل والتاريخ والحالة مطلوبة!', 'error')
        return redirect(url_for('attendance.show_attendance'))

    attendance_date = parse_date(date_str)

    if not attendance_date:
        flash('صيغة التاريخ غير صحيحة!', 'error')
        return redirect(url_for('attendance.show_attendance'))

    try:
        child_id = int(child_id)
        child = Child.query.filter_by(child_id=child_id, user_id=user_id).first()

        if not child:
            flash('الطفل غير موجود أو لا يخص هذا المستخدم.', 'error')
            return redirect(url_for('attendance.show_attendance'))

        existing = Attendance.query.filter_by(
            child_id=child_id,
            date=attendance_date,
            user_id=user_id
        ).first()

        if existing:
            flash('يوجد سجل حضور مسبق لهذا الطفل في نفس التاريخ!', 'error')
            return redirect(url_for('attendance.show_attendance'))

        record = Attendance(
            child_id=child_id,
            date=attendance_date,
            status=status,
            check_in_time=parse_time(check_in_time),
            check_out_time=parse_time(check_out_time),
            notes=notes or None,
            user_id=user_id
        )

        db.session.add(record)
        db.session.commit()

        child_name = f'{child.first_name} {child.last_name}'
        flash(f'تم تسجيل حضور "{child_name}" بنجاح!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في تسجيل الحضور: {str(e)}', 'error')

    return redirect(url_for('attendance.show_attendance'))


@attendance_bp.route('/bulk_attendance', methods=['POST'])
def bulk_attendance():
    user_id = session['user_id']

    date_str = request.form.get('date')
    child_ids = request.form.getlist('child_ids[]')
    statuses = request.form.getlist('statuses[]')
    check_in_times = request.form.getlist('check_in_times[]')
    notes_list = request.form.getlist('notes[]')

    if not date_str:
        flash('التاريخ مطلوب!', 'error')
        return redirect(url_for('attendance.show_attendance'))

    attendance_date = parse_date(date_str)

    if not attendance_date:
        flash('صيغة التاريخ غير صحيحة!', 'error')
        return redirect(url_for('attendance.show_attendance'))

    success_count = 0
    error_count = 0

    try:
        for i, child_id in enumerate(child_ids):
            if i >= len(statuses) or not statuses[i]:
                continue

            child_id = int(child_id)

            child = Child.query.filter_by(child_id=child_id, user_id=user_id).first()
            if not child:
                error_count += 1
                continue

            status = statuses[i]
            check_in_time = check_in_times[i] if i < len(check_in_times) else ''
            notes = notes_list[i] if i < len(notes_list) else ''

            existing = Attendance.query.filter_by(
                child_id=child_id,
                date=attendance_date,
                user_id=user_id
            ).first()

            if existing:
                error_count += 1
                continue

            record = Attendance(
                child_id=child_id,
                date=attendance_date,
                status=status,
                check_in_time=parse_time(check_in_time),
                notes=notes or None,
                user_id=user_id
            )

            db.session.add(record)
            success_count += 1

        db.session.commit()

        if success_count > 0:
            flash(f'تم تسجيل حضور {success_count} طفل بنجاح!', 'success')

        if error_count > 0:
            flash(f'فشل في تسجيل {error_count} من الأطفال لأن لديهم سجلات مسبقة أو لا يخصون هذا المستخدم.', 'warning')

    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في التسجيل الجماعي: {str(e)}', 'error')

    return redirect(url_for('attendance.show_attendance'))


@attendance_bp.route('/update_attendance/<int:id>', methods=['POST'])
def update_attendance(id):
    user_id = session['user_id']

    record = Attendance.query.filter_by(attendance_id=id, user_id=user_id).first()

    if not record:
        flash('سجل الحضور غير موجود!', 'error')
        return redirect(url_for('attendance.show_attendance'))

    child_id = request.form.get('child_id')
    date_str = request.form.get('date')
    status = request.form.get('status')
    check_in_time = request.form.get('check_in_time', '').strip()
    check_out_time = request.form.get('check_out_time', '').strip()
    notes = request.form.get('notes', '').strip()

    if not child_id or not date_str or not status:
        flash('جميع الحقول الأساسية مطلوبة!', 'error')
        return redirect(url_for('attendance.show_attendance'))

    attendance_date = parse_date(date_str)

    if not attendance_date:
        flash('صيغة التاريخ غير صحيحة!', 'error')
        return redirect(url_for('attendance.show_attendance'))

    try:
        child_id = int(child_id)
        child = Child.query.filter_by(child_id=child_id, user_id=user_id).first()

        if not child:
            flash('الطفل غير موجود أو لا يخص هذا المستخدم.', 'error')
            return redirect(url_for('attendance.show_attendance'))

        record.child_id = child_id
        record.date = attendance_date
        record.status = status
        record.check_in_time = parse_time(check_in_time)
        record.check_out_time = parse_time(check_out_time)
        record.notes = notes or None

        db.session.commit()

        child_name = f'{child.first_name} {child.last_name}'
        flash(f'تم تحديث حضور "{child_name}" بنجاح!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في تحديث الحضور: {str(e)}', 'error')

    return redirect(url_for('attendance.show_attendance'))


@attendance_bp.route('/delete_attendance/<int:id>')
def delete_attendance(id):
    user_id = session['user_id']

    record = Attendance.query.filter_by(attendance_id=id, user_id=user_id).first()

    if not record:
        flash('سجل الحضور غير موجود!', 'error')
        return redirect(url_for('attendance.show_attendance'))

    child_name = (
        f'{record.child.first_name} {record.child.last_name}'
        if record.child else 'الطفل'
    )
    record_date = record.date

    try:
        db.session.delete(record)
        db.session.commit()
        flash(f'تم حذف سجل حضور "{child_name}" بتاريخ "{record_date}" بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في حذف سجل الحضور: {str(e)}', 'error')

    return redirect(url_for('attendance.show_attendance'))


@attendance_bp.route('/attendance_report')
def attendance_report():
    user_id = session['user_id']

    start_date = request.args.get('start_date', date.today().strftime('%Y-%m-01'))
    end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
    child_id = request.args.get('child_id')
    class_id = request.args.get('class_id')

    start = parse_date(start_date)
    end = parse_date(end_date)

    try:
        query = Attendance.query.filter(
            Attendance.user_id == user_id,
            Attendance.date.between(start, end)
        )

        if child_id:
            query = query.filter(Attendance.child_id == int(child_id))

        if class_id:
            query = query.join(Child).filter(
                Child.class_id == int(class_id),
                Child.user_id == user_id
            )

        attendance_records = query.order_by(Attendance.date.desc()).all()

        for record in attendance_records:
            record.child_name = (
                f'{record.child.first_name} {record.child.last_name}'
                if record.child else 'غير محدد'
            )
            record.class_name = (
                record.child.classroom.name
                if record.child and record.child.classroom else 'غير محدد'
            )
            record.branch_name = (
                record.child.classroom.branch.name
                if record.child and record.child.classroom and record.child.classroom.branch else 'غير محدد'
            )

        status_summary = []
        for status in ['Present', 'Absent', 'Late']:
            count = Attendance.query.filter(
                Attendance.user_id == user_id,
                Attendance.date.between(start, end),
                Attendance.status == status
            ).count()

            status_summary.append({
                'status': status,
                'count': count
            })

        children = Child.query.filter_by(user_id=user_id, is_active=True).order_by(Child.first_name.asc()).all()
        classes = Class.query.filter_by(user_id=user_id).order_by(Class.name.asc()).all()

        for child in children:
            child.name = f'{child.first_name} {child.last_name}'

    except Exception as e:
        flash(f'خطأ في تقرير الحضور: {str(e)}', 'error')
        attendance_records = []
        status_summary = []
        children = []
        classes = []

    return render_template(
        'attendance_report.html',
        attendance_records=attendance_records,
        status_summary=status_summary,
        children=children,
        classes=classes,
        start_date=start_date,
        end_date=end_date,
        selected_child=child_id,
        selected_class=class_id
    )