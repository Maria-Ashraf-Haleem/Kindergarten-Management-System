#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إنشاء بيانات تجريبية لنظام إدارة الحضانة
"""

import sqlite3
from datetime import datetime, date, timedelta
import random
from db import get_conn, init_db

def create_sample_data():
    """إنشاء بيانات تجريبية للنظام"""
    
    # التأكد من وجود قاعدة البيانات
    init_db()
    
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        print("🚀 بدء إنشاء البيانات التجريبية...")
        
        # حذف البيانات الموجودة (اختياري)
        tables = ['Graduation', 'Fee', 'StaffAttendance', 'Attendance', 
                'Child', 'Staff', 'Parent', 'Subject', 'Class', 'Branch']
        
        for table in tables:
            cur.execute(f'DELETE FROM {table}')
        
        # 1. إنشاء الفروع
        print("📍 إنشاء الفروع...")
        branches_data = [
            ('فرع المعادي', 'شارع 9، المعادي، القاهرة', '02-25555555'),
            ('فرع مدينة نصر', 'شارع عباس العقاد، مدينة نصر، القاهرة', '02-26666666'),
            ('فرع الزمالك', 'شارع 26 يوليو، الزمالك، القاهرة', '02-27777777'),
            ('فرع الإسكندرية', 'شارع فؤاد، الإسكندرية', '03-4888888')
        ]
        
        cur.executemany('INSERT INTO Branch (name, address, phone) VALUES (?, ?, ?)', 
                        branches_data)
        
        # 2. إنشاء الكلاسات
        print("🏫 إنشاء الكلاسات...")
        classes_data = [
            ('الحضانة الصغرى', 1, 15, '2-3 سنوات'),
            ('الحضانة الوسطى', 1, 20, '3-4 سنوات'),
            ('الحضانة الكبرى', 1, 25, '4-5 سنوات'),
            ('التمهيدي', 1, 20, '5-6 سنوات'),
            ('الحضانة الصغرى', 2, 15, '2-3 سنوات'),
            ('الحضانة الوسطى', 2, 20, '3-4 سنوات'),
            ('الحضانة الكبرى', 2, 25, '4-5 سنوات'),
            ('الحضانة الصغرى', 3, 18, '2-3 سنوات'),
            ('الحضانة الوسطى', 3, 22, '3-4 سنوات'),
            ('التمهيدي', 3, 20, '5-6 سنوات')
        ]
        
        cur.executemany('INSERT INTO Class (name, branch_id, max_capacity, age_group) VALUES (?, ?, ?, ?)', 
                        classes_data)
        
        # 3. إنشاء أولياء الأمور
        print("👨‍👩‍👧‍👦 إنشاء أولياء الأمور...")
        parents_data = [
            ('أحمد', 'محمد', '01012345678', 'ahmed@example.com', 'المعادي، القاهرة', '01098765432'),
            ('فاطمة', 'علي', '01123456789', 'fatma@example.com', 'مدينة نصر، القاهرة', '01087654321'),
            ('محمد', 'حسن', '01234567890', 'mohamed@example.com', 'الزمالك، القاهرة', '01076543210'),
            ('عائشة', 'أحمد', '01345678901', 'aisha@example.com', 'المهندسين، القاهرة', '01065432109'),
            ('يوسف', 'إبراهيم', '01456789012', 'youssef@example.com', 'الدقي، القاهرة', '01054321098'),
            ('مريم', 'عبدالله', '01567890123', 'mariam@example.com', 'الإسكندرية', '01043210987'),
            ('خالد', 'محمود', '01678901234', 'khaled@example.com', 'المعادي، القاهرة', '01032109876'),
            ('نور', 'سالم', '01789012345', 'nour@example.com', 'مدينة نصر، القاهرة', '01021098765'),
            ('عمر', 'فاروق', '01890123456', 'omar@example.com', 'الزمالك، القاهرة', '01010987654'),
            ('زينب', 'طارق', '01901234567', 'zeinab@example.com', 'المهندسين، القاهرة', '01009876543')
        ]
        
        cur.executemany('''INSERT INTO Parent (first_name, last_name, phone, email, address, emergency_contact) 
                        VALUES (?, ?, ?, ?, ?, ?)''', parents_data)
        
        # 4. إنشاء الأطفال
        print("👶 إنشاء الأطفال...")
        children_names = [
            ('علي', 'أحمد', 'Male'),
            ('سارة', 'فاطمة', 'Female'),
            ('يوسف', 'محمد', 'Male'),
            ('آية', 'عائشة', 'Female'),
            ('محمد', 'يوسف', 'Male'),
            ('فاطمة', 'مريم', 'Female'),
            ('أحمد', 'خالد', 'Male'),
            ('نور', 'نور', 'Female'),
            ('حسن', 'عمر', 'Male'),
            ('زينب', 'زينب', 'Female'),
            ('إبراهيم', 'أحمد', 'Male'),
            ('مريم', 'فاطمة', 'Female'),
            ('عبدالله', 'محمد', 'Male'),
            ('عائشة', 'عائشة', 'Female'),
            ('طارق', 'يوسف', 'Male')
        ]
        
        children_data = []
        for i, (first_name, last_name, gender) in enumerate(children_names, 1):
            birth_date = date.today() - timedelta(days=random.randint(730, 2190))  # 2-6 سنوات
            parent_id = random.randint(1, 10)
            class_id = random.randint(1, 10)
            enrollment_date = date.today() - timedelta(days=random.randint(30, 365))
            
            children_data.append((
                first_name, last_name, birth_date, gender, parent_id, class_id,
                f'معلومات طبية للطفل {first_name}', enrollment_date, 1
            ))
        
        cur.executemany('''INSERT INTO Child (first_name, last_name, date_of_birth, gender, parent_id, class_id, 
                        medical_info, enrollment_date, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        children_data)
        
        # 5. إنشاء الموظفين
        print("👩‍🏫 إنشاء الموظفين...")
        staff_data = [
            ('سمية', 'محمد', 'مديرة', 1, '01155555555', 'somaya@kindergarten.com', date.today() - timedelta(days=1000), 8000, 1),
            ('نادية', 'أحمد', 'معلمة', 1, '01144444444', 'nadia@kindergarten.com', date.today() - timedelta(days=800), 6000, 1),
            ('ريم', 'علي', 'معلمة', 1, '01133333333', 'reem@kindergarten.com', date.today() - timedelta(days=600), 5500, 1),
            ('هند', 'حسن', 'ممرضة', 1, '01122222222', 'hind@kindergarten.com', date.today() - timedelta(days=400), 4500, 1),
            ('أميرة', 'سالم', 'معلمة', 2, '01111111111', 'amira@kindergarten.com', date.today() - timedelta(days=700), 5800, 1),
            ('لميس', 'فاروق', 'معلمة', 2, '01100000000', 'lamees@kindergarten.com', date.today() - timedelta(days=500), 5600, 1),
            ('منى', 'طارق', 'مساعدة', 2, '01199999999', 'mona@kindergarten.com', date.today() - timedelta(days=300), 4000, 1),
            ('سلمى', 'إبراهيم', 'معلمة', 3, '01188888888', 'salma@kindergarten.com', date.today() - timedelta(days=650), 5700, 1)
        ]
        
        cur.executemany('''INSERT INTO Staff (first_name, last_name, position, branch_id, phone, email, 
                        hire_date, salary, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', staff_data)
        
        # 6. إنشاء المواد
        print("📚 إنشاء المواد...")
        subjects_data = [
            ('اللغة العربية', 'تعليم أساسيات اللغة العربية والقراءة'),
            ('الرياضيات', 'تعليم الأرقام والعمليات الحسابية البسيطة'),
            ('الأنشطة الفنية', 'الرسم والتلوين والأشغال اليدوية'),
            ('التربية البدنية', 'الألعاب الحركية والتمارين الرياضية'),
            ('العلوم', 'استكشاف الطبيعة والعلوم البسيطة'),
            ('الموسيقى', 'تعليم الأناشيد والإيقاع'),
            ('اللغة الإنجليزية', 'تعليم أساسيات اللغة الإنجليزية'),
            ('التربية الإسلامية', 'تعليم القيم والآداب الإسلامية')
        ]
        
        cur.executemany('INSERT INTO Subject (name, description) VALUES (?, ?)', subjects_data)
        
        # 7. إنشاء سجلات حضور للأطفال
        print("📝 إنشاء سجلات حضور الأطفال...")
        attendance_data = []
        for child_id in range(1, 16):  # 15 طفل
            for day_offset in range(30):  # آخر 30 يوم
                attendance_date = date.today() - timedelta(days=day_offset)
                # تجنب العطل (الجمعة والسبت)
                if attendance_date.weekday() < 5:  # من الأحد إلى الخميس
                    status = random.choices(['Present', 'Absent', 'Late'], weights=[85, 10, 5])[0]
                    if status != 'Absent':
                        check_in = f"{random.randint(7, 9)}:{random.randint(0, 59):02d}"
                        check_out = f"{random.randint(14, 16)}:{random.randint(0, 59):02d}" if status == 'Present' else None
                    else:
                        check_in = check_out = None
                    
                    attendance_data.append((child_id, attendance_date, status, check_in, check_out, ''))
        
        cur.executemany('''INSERT INTO Attendance (child_id, date, status, check_in_time, check_out_time, notes) 
                        VALUES (?, ?, ?, ?, ?, ?)''', attendance_data)
        
        # 8. إنشاء سجلات حضور للموظفين
        print("📋 إنشاء سجلات حضور الموظفين...")
        staff_attendance_data = []
        for staff_id in range(1, 9):  # 8 موظفين
            for day_offset in range(30):  # آخر 30 يوم
                attendance_date = date.today() - timedelta(days=day_offset)
                if attendance_date.weekday() < 5:  # من الأحد إلى الخميس
                    status = random.choices(['Present', 'Absent', 'Late'], weights=[90, 5, 5])[0]
                    if status != 'Absent':
                        check_in = f"{random.randint(6, 8)}:{random.randint(0, 59):02d}"
                        check_out = f"{random.randint(15, 17)}:{random.randint(0, 59):02d}"
                    else:
                        check_in = check_out = None
                    
                    staff_attendance_data.append((staff_id, attendance_date, check_in, check_out, status, ''))
        
        cur.executemany('''INSERT INTO StaffAttendance (staff_id, date, check_in_time, check_out_time, status, notes) 
                        VALUES (?, ?, ?, ?, ?, ?)''', staff_attendance_data)
        
        # 9. إنشاء الرسوم
        print("💰 إنشاء الرسوم...")
        fee_data = []
        for child_id in range(1, 16):  # 15 طفل
            for month in range(1, 7):  # 6 أشهر
                due_date = date(2024, month, 1)
                amount = random.choice([1500, 1800, 2000, 2200])  # رسوم مختلفة
                
                # تحديد حالة الدفع
                if month < 5:  # الأشهر السابقة مدفوعة غالباً
                    status = random.choices(['Paid', 'Overdue'], weights=[85, 15])[0]
                    paid_date = due_date + timedelta(days=random.randint(-5, 15)) if status == 'Paid' else None
                    payment_method = random.choice(['Cash', 'Card', 'Transfer']) if status == 'Paid' else None
                else:  # الأشهر الحالية قد تكون معلقة
                    status = random.choices(['Paid', 'Pending', 'Overdue'], weights=[60, 30, 10])[0]
                    paid_date = due_date + timedelta(days=random.randint(-5, 10)) if status == 'Paid' else None
                    payment_method = random.choice(['Cash', 'Card', 'Transfer']) if status == 'Paid' else None
                
                fee_data.append((child_id, amount, due_date, paid_date, payment_method, status, ''))
        
        cur.executemany('''INSERT INTO Fee (child_id, amount, due_date, paid_date, payment_method, status, notes) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)''', fee_data)
        
        # 10. إنشاء سجلات التخرج
        print("🎓 إنشاء سجلات التخرج...")
        graduation_data = [
            (1, date(2024, 6, 15), 1, 'ممتاز', 'طفل متميز في جميع الأنشطة'),
            (2, date(2024, 6, 15), 1, 'جيد جداً', 'تفاعل جيد مع الأنشطة التعليمية'),
            (3, date(2024, 6, 15), 0, 'جيد', 'يحتاج إلى مزيد من التشجيع'),
        ]
        
        cur.executemany('''INSERT INTO Graduation (child_id, graduation_date, certificate_issued, final_grade, comments) 
                        VALUES (?, ?, ?, ?, ?)''', graduation_data)
        
        conn.commit()
        print("✅ تم إنشاء البيانات التجريبية بنجاح!")
        print("\n📊 إحصائيات البيانات المُنشأة:")
        
        # عرض الإحصائيات
        stats_queries = [
            ('الفروع', 'SELECT COUNT(*) FROM Branch'),
            ('الكلاسات', 'SELECT COUNT(*) FROM Class'),
            ('أولياء الأمور', 'SELECT COUNT(*) FROM Parent'),
            ('الأطفال', 'SELECT COUNT(*) FROM Child'),
            ('الموظفون', 'SELECT COUNT(*) FROM Staff'),
            ('المواد', 'SELECT COUNT(*) FROM Subject'),
            ('سجلات حضور الأطفال', 'SELECT COUNT(*) FROM Attendance'),
            ('سجلات حضور الموظفين', 'SELECT COUNT(*) FROM StaffAttendance'),
            ('الرسوم', 'SELECT COUNT(*) FROM Fee'),
            ('التخرجات', 'SELECT COUNT(*) FROM Graduation')
        ]
        
        for name, query in stats_queries:
            cur.execute(query)
            count = cur.fetchone()[0]
            print(f"   • {name}: {count}")
            
    except Exception as e:
        print(f"❌ خطأ في إنشاء البيانات: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    create_sample_data()