from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from functools import wraps
from extensions import db
from models import User, UPSCPaper
from sqlalchemy import or_
from models import Syllabus ,Feedback


admin_bp = Blueprint('admin', __name__)

# Admin session check decorator
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please login as admin to access this page.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@admin_bp.route('/dashboard')
@admin_login_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('admin.login'))   # Use function name, not template filename

@admin_bp.route('/manage_users')
@admin_login_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@admin_login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    # Check if AJAX request by header
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON response to avoid page reload
        return jsonify({'success': True, 'message': 'User deleted successfully.'})
    else:
        # Fallback for normal form POST submit
        flash("User deleted successfully.", "success")
        return redirect(url_for('admin.manage_users'))
    


@admin_bp.route('/manage_pyqs')
@admin_login_required
def manage_pyqs():
    exam_type = request.args.get('exam_type', '').strip()
    paper_type = request.args.get('paper_type', '').strip()
    sub_paper_type = request.args.get('sub_paper_type', '').strip()
    year = request.args.get('year', '').strip()

    query = UPSCPaper.query

    if exam_type:
        query = query.filter(UPSCPaper.exam_type.ilike(f"%{exam_type}%"))
    if paper_type:
        query = query.filter(UPSCPaper.paper_type.ilike(f"%{paper_type}%"))
    if sub_paper_type:
        query = query.filter(UPSCPaper.sub_paper_type.ilike(f"%{sub_paper_type}%"))
    if year:
        if year.isdigit():
            query = query.filter(UPSCPaper.year == int(year))

    pyqs = query.all()
    return render_template('admin/manage_pyqs.html', pyqs=pyqs)

@admin_bp.route('/add_pyq', methods=['POST'])
@admin_login_required
def add_pyq():
    exam_type = request.form['exam_type'].strip().lower()
    paper_type = request.form['paper_type'].strip().lower()
    sub_paper_type = request.form.get('sub_paper_type', '').strip().lower() or None
    year = request.form['year']
    pdf_link = request.form['pdf_link']

    existing_pyq = UPSCPaper.query.filter_by(
        exam_type=exam_type,
        paper_type=paper_type,
        sub_paper_type=sub_paper_type,
        year=int(year)
    ).first()

    if existing_pyq:
        existing_pyq.pdf_link = pdf_link
        db.session.commit()
        flash("PDF updated in existing row.", "info")
    else:
        new_pyq = UPSCPaper(
            exam_type=exam_type,
            paper_type=paper_type,
            sub_paper_type=sub_paper_type,
            year=int(year),
            pdf_link=pdf_link
        )
        db.session.add(new_pyq)
        db.session.commit()
        flash("PYQ added successfully!", "success")

    return redirect(url_for('admin.manage_pyqs'))

@admin_bp.route('/edit-pyq/<int:pyq_id>', methods=['POST'])
@admin_login_required
def edit_pyq(pyq_id):
    pyq = UPSCPaper.query.get_or_404(pyq_id)
    data = request.form

    if 'pdf_link' in data:
        pyq.pdf_link = data['pdf_link']
    if 'year' in data and data['year'].isdigit():
        pyq.year = int(data['year'])

    db.session.commit()
    return '', 204

@admin_bp.route('/delete-pyq/<int:pyq_id>', methods=['POST'])
@admin_login_required
def delete_pyq(pyq_id):
    pyq = UPSCPaper.query.get_or_404(pyq_id)
    db.session.delete(pyq)
    db.session.commit()
    flash("PYQ deleted successfully!", "success")
    return redirect(url_for('admin.manage_pyqs'))







@admin_bp.route('/manage_syllabus', methods=['GET'])
@admin_login_required
def manage_syllabus():
    syllabi = Syllabus.query.order_by(Syllabus.year.desc()).all()
    return render_template('admin/manage_syllabus.html', syllabi=syllabi)

@admin_bp.route('/add_syllabus', methods=['POST'])
@admin_login_required
def add_syllabus():
    data = request.form
    exam_type = data.get('exam_type', '').strip()
    paper_type = data.get('paper_type', '').strip()
    year = data.get('year', '').strip()
    link = data.get('link', '').strip()

    if not (exam_type and paper_type and year.isdigit() and link):
        flash("Please fill all fields correctly to add syllabus.", "error")
        return redirect(url_for('admin.manage_syllabus'))

    new_syllabus = Syllabus(
        exam_type=exam_type,
        paper_type=paper_type,
        year=int(year),
        link=link
    )
    db.session.add(new_syllabus)
    db.session.commit()
    flash("Syllabus added successfully!", "success")
    return redirect(url_for('admin.manage_syllabus'))

@admin_bp.route('/edit_syllabus/<int:syllabus_id>', methods=['POST'])
@admin_login_required
def edit_syllabus(syllabus_id):
    syllabus = Syllabus.query.get_or_404(syllabus_id)
    data = request.form

    exam_type = data.get('exam_type', '').strip()
    paper_type = data.get('paper_type', '').strip()
    year = data.get('year', '').strip()
    link = data.get('link', '').strip()

    if not (exam_type and paper_type and year.isdigit() and link):
        flash("Please fill all fields correctly to update syllabus.", "error")
        return redirect(url_for('admin.manage_syllabus'))

    syllabus.exam_type = exam_type
    syllabus.paper_type = paper_type
    syllabus.year = int(year)
    syllabus.link = link

    db.session.commit()
    flash("Syllabus updated successfully!", "success")
    return redirect(url_for('admin.manage_syllabus'))

@admin_bp.route('/delete_syllabus/<int:syllabus_id>', methods=['POST'])
@admin_login_required
def delete_syllabus(syllabus_id):
    syllabus = Syllabus.query.get_or_404(syllabus_id)
    db.session.delete(syllabus)
    db.session.commit()
    flash("Syllabus deleted successfully!", "success")
    return redirect(url_for('admin.manage_syllabus'))




@admin_bp.route('/manage_feedbacks')
@admin_login_required
def manage_feedbacks():
    feedbacks = Feedback.query.order_by(Feedback.submitted_at.desc()).all()
    return render_template('admin/manage_feedbacks.html', feedbacks=feedbacks)