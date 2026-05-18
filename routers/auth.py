from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not full_name or not email or not password or not confirm_password:
            flash('من فضلك املأ جميع الحقول المطلوبة.', 'error')
            return redirect(url_for('auth.signup'))

        if len(password) < 6:
            flash('كلمة المرور يجب ألا تقل عن 6 أحرف.', 'error')
            return redirect(url_for('auth.signup'))

        if password != confirm_password:
            flash('كلمة المرور وتأكيد كلمة المرور غير متطابقين.', 'error')
            return redirect(url_for('auth.signup'))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('هذا البريد الإلكتروني مستخدم بالفعل.', 'error')
            return redirect(url_for('auth.signup'))

        user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password),
            role='admin'
        )

        try:
            db.session.add(user)
            db.session.commit()
            flash('تم إنشاء الحساب بنجاح، يمكنك تسجيل الدخول الآن.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إنشاء الحساب: {str(e)}', 'error')
            return redirect(url_for('auth.signup'))

    return render_template('auth/signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('من فضلك أدخل البريد الإلكتروني وكلمة المرور.', 'error')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة.', 'error')
            return redirect(url_for('auth.login'))

        session.clear()
        session['user_id'] = user.user_id
        session['full_name'] = user.full_name
        session['email'] = user.email
        session['role'] = user.role

        flash(f'مرحباً {user.full_name}، تم تسجيل الدخول بنجاح.', 'success')
        return redirect(url_for('index'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('auth.login'))