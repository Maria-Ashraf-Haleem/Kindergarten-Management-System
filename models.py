from datetime import datetime, date
from extensions import db


class Branch(db.Model):
    __tablename__ = 'branches'

    branch_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255))
    phone = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    classes = db.relationship('Class', back_populates='branch')
    staff_members = db.relationship('Staff', back_populates='branch')


class Class(db.Model):
    __tablename__ = 'classes'

    class_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    name = db.Column(db.String(120), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.branch_id'), nullable=True)
    max_capacity = db.Column(db.Integer, default=25)
    age_group = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    branch = db.relationship('Branch', back_populates='classes')
    children = db.relationship('Child', back_populates='classroom')


class Parent(db.Model):
    __tablename__ = 'parents'

    parent_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    address = db.Column(db.String(255))
    emergency_contact = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    children = db.relationship('Child', back_populates='parent')


class Child(db.Model):
    __tablename__ = 'children'

    child_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.parent_id'), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=True)
    medical_info = db.Column(db.Text)
    enrollment_date = db.Column(db.Date, default=date.today)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    parent = db.relationship('Parent', back_populates='children')
    classroom = db.relationship('Class', back_populates='children')
    attendance_records = db.relationship('Attendance', back_populates='child', cascade='all, delete-orphan')
    fees = db.relationship('Fee', back_populates='child', cascade='all, delete-orphan')


class Staff(db.Model):
    __tablename__ = 'staff'

    staff_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.branch_id'), nullable=True)
    phone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    hire_date = db.Column(db.Date, default=date.today)
    salary = db.Column(db.Numeric(10, 2))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    branch = db.relationship('Branch', back_populates='staff_members')


class Attendance(db.Model):
    __tablename__ = 'attendance'

    attendance_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    child_id = db.Column(db.Integer, db.ForeignKey('children.child_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Present')
    check_in_time = db.Column(db.Time)
    check_out_time = db.Column(db.Time)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    child = db.relationship('Child', back_populates='attendance_records')


class Fee(db.Model):
    __tablename__ = 'fees'

    fee_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    child_id = db.Column(db.Integer, db.ForeignKey('children.child_id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    paid_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Pending')
    payment_method = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    child = db.relationship('Child', back_populates='fees')


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), default='admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    branches = db.relationship('Branch', backref='owner')
    classes = db.relationship('Class', backref='owner')
    parents = db.relationship('Parent', backref='owner')
    children = db.relationship('Child', backref='owner')
    staff_members = db.relationship('Staff', backref='owner')
    attendance_records = db.relationship('Attendance', backref='owner')
    fees = db.relationship('Fee', backref='owner')