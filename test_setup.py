#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت اختبار التشغيل وتشخيص المشاكل
"""

import sys
import os
from db import get_conn, init_db

def test_database():
    """اختبار الاتصال بقاعدة البيانات"""
    print("🔍 اختبار قاعدة البيانات...")
    
    try:
        # إنشاء قاعدة البيانات
        init_db()
        print("✅ تم إنشاء قاعدة البيانات بنجاح")
        
        # اختبار الاتصال
        conn = get_conn()
        cur = conn.cursor()
        
        # اختبار الجداول
        tables_to_check = ['Branch', 'Class', 'Parent', 'Child', 'Staff', 'Fee']
        
        for table in tables_to_check:
            cur.execute(f'SELECT COUNT(*) FROM {table}')
            count = cur.fetchone()[0]
            print(f"   📊 جدول {table}: {count} سجل")
        
        conn.close()
        print("✅ اختبار قاعدة البيانات تم بنجاح")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في قاعدة البيانات: {e}")
        return False

def test_imports():
    """اختبار استيراد الملفات"""
    print("\n🔍 اختبار استيراد الملفات...")
    
    required_files = [
        'app.py',
        'db.py',
        'routersclasses.py',
        'routersfee.py',
        'class.html',
        'fees.html',
        'base.html',
        'index.html'
    ]
    
    missing_files = []
    
    for file in required_files:
        if file.endswith('.html'):
            file_path = os.path.join('templates', file)
        else:
            file_path = file
            
        if os.path.exists(file_path):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - مفقود!")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  الملفات المفقودة: {', '.join(missing_files)}")
        return False
    else:
        print("✅ جميع الملفات موجودة")
        return True

def test_routes():
    """اختبار المسارات"""
    print("\n🔍 اختبار استيراد المسارات...")
    
    try:
        # اختبار استيراد المسارات
        from routersclasses import classes_bp
        print("   ✅ routersclasses.py")
        
        from routersfee import fee_bp
        print("   ✅ routersfee.py")
        
        print("✅ جميع المسارات تم استيرادها بنجاح")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في استيراد المسارات: {e}")
        return False

def create_sample_data():
    """إنشاء بيانات تجريبية بسيطة"""
    print("\n🚀 إنشاء بيانات تجريبية...")
    
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        # إضافة فرع تجريبي
        cur.execute("INSERT OR IGNORE INTO Branch (branch_id, name, address) VALUES (1, 'الفرع الرئيسي', 'القاهرة')")
        
        # إضافة كلاس تجريبي
        cur.execute("INSERT OR IGNORE INTO Class (class_id, name, branch_id, max_capacity, age_group) VALUES (1, 'الحضانة الصغرى', 1, 20, '3-4 سنوات')")
        
        # إضافة ولي أمر تجريبي
        cur.execute("INSERT OR IGNORE INTO Parent (parent_id, first_name, last_name, phone) VALUES (1, 'أحمد', 'محمد', '01012345678')")
        
        # إضافة طفل تجريبي
        cur.execute("INSERT OR IGNORE INTO Child (child_id, first_name, last_name, parent_id, class_id, gender, is_active) VALUES (1, 'علي', 'أحمد', 1, 1, 'Male', 1)")
        
        # إضافة رسوم تجريبية
        cur.execute("INSERT OR IGNORE INTO Fee (fee_id, child_id, amount, due_date, status) VALUES (1, 1, 1500.00, '2024-12-01', 'Pending')")
        
        conn.commit()
        conn.close()
        
        print("✅ تم إنشاء البيانات التجريبية")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء البيانات: {e}")
        return False

def main():
    """الدالة الرئيسية للاختبار"""
    print("🚀 بدء اختبارات النظام...\n")
    
    # اختبار المكونات
    tests = [
        ("قاعدة البيانات", test_database),
        ("الملفات", test_imports),
        ("المسارات", test_routes),
        ("البيانات التجريبية", create_sample_data)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        print()
    
    # النتيجة النهائية
    print("="*50)
    print(f"📊 النتيجة النهائية: {passed}/{total} اختبار نجح")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت! يمكنك تشغيل التطبيق الآن")
        print("💡 لتشغيل التطبيق: python app.py")
    else:
        print("⚠️  هناك مشاكل تحتاج إلى حل")
        
    print("="*50)

if __name__ == '__main__':
    main()