from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_conn

graduation_bp = Blueprint('graduation', __name__)

@graduation_bp.route('/graduation')
def show_graduation():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('''
            SELECT g.*, c.first_name || " " || c.last_name as child_name,
                    cl.name as class_name
            FROM Graduation g
            LEFT JOIN Child c ON g.child_id = c.child_id
            LEFT JOIN Class cl ON c.class_id = cl.class_id
            ORDER BY g.graduation_date DESC, g.created_at DESC
        ''')
        graduations = cur.fetchall()
        
        # جلب الأطفال للاختيار
        cur.execute('SELECT child_id, first_name || " " || last_name as name FROM Child')
        children = cur.fetchall()
        
    except Exception as e:
        flash(f'خطأ في جلب البيانات: {str(e)}', 'error')
        graduations = []
        children = []
    finally:
        conn.close()
    
    return render_template('graduation.html', graduations=graduations, children=children)