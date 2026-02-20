import os
import json
import requests
import urllib.parse
from datetime import datetime
import uuid
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import (
    Flask, flash, render_template, request, redirect,
    session, url_for, jsonify, send_file, get_flashed_messages
)
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user
)
from urllib.parse import urlparse
from bs4 import BeautifulSoup 
from extensions import db
import urllib3
from models import User, Feedback, UPSCPaper, Syllabus 


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")




DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Railway case
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://")
else:
    # Local development fallback
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "upsc_app")
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"



app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app) 

with app.app_context():
    db.create_all()

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from admin.routes import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Session token validation before each request
@app.before_request
def validate_session():
    if current_user.is_authenticated:
        session_token = session.get('session_token')
        if session_token != current_user.session_token:
            logout_user()
            session.pop('session_token', None)
            flash("Logged out due to session invalidation.", "warning")
            return redirect(url_for('login'))

# Home
@app.route('/')
def home():
    return render_template('index.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        get_flashed_messages()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        new_user.session_token = str(uuid.uuid4())
        db.session.commit()
        login_user(new_user)
        session['session_token'] = new_user.session_token

        return redirect(url_for('dashboard'))

    return render_template('register.html')


# Define your admin credentials (or fetch from config / DB later)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")



# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session.pop('_flashes', None) 

            session['admin_logged_in'] = True

            return redirect(url_for('admin.dashboard'))  

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session.pop('_flashes', None)

            user.session_token = str(uuid.uuid4())
            db.session.commit()
            db.session.refresh(user)

            login_user(user)
            session['session_token'] = user.session_token
           
            return redirect(url_for('dashboard'))

        session.pop('_flashes', None)
        flash("Invalid credentials", "danger")

    return render_template('login.html')


# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Profile
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# Update Profile
@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    new_username = request.form.get('new_username')
    new_email = request.form.get('new_email')

    if not new_username or not new_email:
        flash("Both fields are required.", "danger")
        return redirect(url_for('profile'))

    current_user.username = new_username
    current_user.email = new_email
    db.session.commit()
   
    return redirect(url_for('profile'))


# Logout
@app.route('/logout', methods=['POST'])
@login_required
def logout():

    session.pop('_flashes', None)
    session.pop('admin_logged_in', None)

    if current_user.is_authenticated:
        current_user.session_token = None
        db.session.commit()

    logout_user()

    session.pop('session_token', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))


@app.route("/settings")
@login_required  
def settings():
    return render_template("settings.html")

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    errors = {}

    if not check_password_hash(current_user.password, current_password):
        errors['current_password'] = "Current password is incorrect."

    if len(new_password) < 6:
        errors['new_password'] = "New password must be at least 6 characters."

    if new_password != confirm_password:
        errors['confirm_password'] = "New passwords do not match."

    if errors:
        return jsonify(success=False, errors=errors)

    current_user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify(success=True, message="Password updated successfully.")


@app.route('/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    name = request.form.get('name')
    message = request.form.get('message')

    errors = {}

    if not name or len(name.strip()) == 0:
        errors['name'] = "Name is required."

    if not message or len(message.strip()) == 0:
        errors['message'] = "Feedback message is required."

    if errors:
       return render_template('settings.html', errors=errors, form_data=request.form, open_form='feedback')

    new_feedback = Feedback(name=name, message=message)
    db.session.add(new_feedback)
    db.session.commit()

    flash("Thank you for your feedback!", "success")
    return redirect(url_for('settings'))


@app.route('/syllabus')
@login_required
def syllabus_main():
    """Main syllabus page that asks users to select an exam type"""
    return render_template('syllabus_main.html')

@app.route('/syllabus/select_exam_type')
@login_required
def syllabus_select_exam_type():
    """Page to select exam type (prelims or mains)"""
    return render_template('syllabus_select_exam_type.html')

@app.route('/syllabus/select_paper_type')
@login_required
def syllabus_select_paper_type():

    exam_type = request.args.get('exam_type')
    if not exam_type:
        return redirect(url_for('syllabus_main'))

    paper_types = db.session.query(Syllabus.paper_type)\
        .filter_by(exam_type=exam_type)\
        .distinct().all()

    paper_types = [{"paper_type": row[0]} for row in paper_types]

    return render_template(
        'syllabus_select_paper_type.html',
        exam_type=exam_type,
        paper_types=paper_types
    )

@app.route('/syllabus/show_syllabus')
@login_required
def syllabus_show_syllabus():

    exam_type = request.args.get('exam_type')
    paper_type = request.args.get('paper_type')

    if not exam_type or not paper_type:
        return redirect(url_for('syllabus_main'))

    syllabi = Syllabus.query.filter_by(
        exam_type=exam_type,
        paper_type=paper_type
    ).order_by(Syllabus.year.desc()).all()

    return render_template(
        'syllabus_show_syllabus.html',
        syllabi=syllabi,
        exam_type=exam_type,
        paper_type=paper_type
    )


@app.route('/syllabus/access/<int:syllabus_id>')
@login_required
def access_syllabus(syllabus_id):
    syllabus = Syllabus.query.get(syllabus_id)

    if not syllabus or not syllabus.link:
        return "Syllabus PDF not found", 404

    return redirect(url_for('static', filename=syllabus.link))




API_KEY = os.environ.get("API_KEY")
BASE_URL = 'https://newsapi.org/v2'

bookmarks = []
categories = ['general', 'business', 'entertainment', 'health', 'science', 'sports', 'technology']
regions = {'india': 'in', 'world': 'us'}

category_keywords = {
    'general': 'India',
    'business': 'India business OR economy OR market',
    'entertainment': 'India entertainment OR Bollywood OR movies',
    'health': 'India health OR medicine OR healthcare',
    'science': 'India science OR research OR technology',
    'sports': 'India sports OR cricket OR football',
    'technology': 'India technology OR gadgets OR IT',
}

def get_news(endpoint, params, limit=12):
    """Generic function to fetch news with fallback and filtering"""
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=5)
        if response.status_code != 200:
            print("API Error:", response.json().get('message'))
            return []
        articles = response.json().get('articles', [])
        # Sort articles preferring those with images
        return sorted(articles, key=lambda x: x.get('urlToImage') is not None, reverse=True)[:limit]
    except Exception as e:
        print("Fetch failed:", str(e))
        return []

def get_top_headlines(category='general', country='in', limit=12):
    """Get top headlines for a category & country (used for world news)"""
    params = {'apiKey': API_KEY, 'pageSize': limit, 'country': country}
    if category and category != 'general':
        params['category'] = category
    return get_news('top-headlines', params, limit)

def get_india_news(category='general', limit=12):
    """Get Indian news with category keywords using everything endpoint"""
    query = category_keywords.get(category, 'India')
    params = {
        'apiKey': API_KEY,
        'q': query,
        'language': 'en',
        'pageSize': limit,
        'sortBy': 'publishedAt'
    }
    return get_news('everything', params, limit)

@app.route('/current_affairs')
@login_required
def current_affairs():
    return redirect(url_for('news_view', region='india', category='general'))

@app.route('/<region>/', defaults={'category': 'general'})
@app.route('/<region>/<category>')
def news_view(region, category):
    """Unified route for region + category news"""
    if region not in regions or category not in categories:
        return redirect(url_for('news_view', region='india', category='general'))

    if region == 'india':
        news_data = get_india_news(category, limit=12)
        top_headlines = news_data[:5]
    else:
        country_code = regions[region]
        top_headlines = get_top_headlines(category, country_code, limit=5)
        news_data = get_top_headlines(category, country_code, limit=12)

    return render_template(
        'CA_index.html',
        categories=categories,
        selected_category=category,
        selected_region=region,
        top_headlines=top_headlines,
        news_data=news_data
    )

@app.route('/bookmark', methods=['POST'])
@login_required
def bookmark():
    article = {
        'title': request.form['title'],
        'url': request.form['url'],
        'image': request.form.get('image', ''),
        'description': request.form.get('description', ''),
        'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    if not any(b['url'] == article['url'] for b in bookmarks):
        bookmarks.append(article)
    return redirect(request.referrer or url_for('current_affairs'))

@app.route('/bookmarks')
@login_required
def show_bookmarks():
    return render_template('CA_bookmarks.html', bookmarks=bookmarks)

@app.route('/remove_bookmark', methods=['POST'])
def remove_bookmark():
    global bookmarks
    url = request.form['url']
    bookmarks = [b for b in bookmarks if b['url'] != url]
    return redirect(url_for('show_bookmarks'))


def load_topics():
    
        with open('data/static_gk_topics.json', 'r') as file:
            return json.load(file)

topic_icons = {
    "History": "fa-landmark",
    "Geography": "fa-globe-asia",
    "Polity": "fa-balance-scale",
    "Economics": "fa-chart-line",
    "Art & Culture": "fa-palette",
    "Science & Tech": "fa-microscope",
    "Environment": "fa-leaf",
    "Current Affairs": "fa-newspaper",
}

@app.route('/static_gk')
@login_required
def static_gk():

    topics_data = load_topics()
    formatted_topics = []
    for category, items in topics_data.items():
        if items and len(items) > 0:
            icon = topic_icons.get(category, "fa-book")  
            formatted_topics.append({
                "name": category,
                "icon": icon,
                "link": items[0]["link"]
            })
    
    return render_template('static_gk.html', topics=formatted_topics)


with open("data/NCERTdata.json") as f:
    ncert_data = json.load(f)

@app.route("/ncert")
@login_required
def class_select():
    classes = list(ncert_data.keys())
    return render_template("NCERT_classes.html", classes=classes)

@app.route("/ncert/<selected_class>")

def subject_select(selected_class):
    if selected_class not in ncert_data:
        return "Invalid class", 404
    subjects = list(ncert_data[selected_class].keys())
    return render_template("NCERT_subject.html", selected_class=selected_class, subjects=subjects)

@app.route("/ncert/<selected_class>/<subject>")
def book_select(selected_class, subject):
    data = ncert_data.get(selected_class, {}).get(subject)
    if isinstance(data, dict):
        return render_template("NCERT_booksSelect.html", selected_class=selected_class, subject=subject, books=data)
    elif isinstance(data, str):
        return redirect(data)
    return render_template("NCERT_booksSelect.html", selected_class=selected_class, subject=subject, data=data)

@app.route('/pyq_examtype')
@login_required
def pyq_examtype():
    exam_types = db.session.query(UPSCPaper.exam_type).distinct().all()
    exam_types = [row[0] for row in exam_types]
    return render_template('pyq_examtype.html', exam_types=exam_types)


@app.route('/pyq_papertype/<exam_type>')
@login_required
def pyq_papertype(exam_type):

    paper_types = db.session.query(UPSCPaper.paper_type)\
        .filter_by(exam_type=exam_type)\
        .distinct().all()

    paper_types = [row[0] for row in paper_types]

    return render_template(
        'pyq_papertype.html',
        exam_type=exam_type,
        paper_types=paper_types
    )

@app.route('/pyq_year/<exam_type>/<paper_type>')
@login_required
def pyq_year(exam_type, paper_type):

    sub_papers = db.session.query(UPSCPaper.sub_paper_type)\
        .filter(
            UPSCPaper.exam_type == exam_type,
            UPSCPaper.paper_type == paper_type,
            UPSCPaper.sub_paper_type.isnot(None)
        ).distinct().all()

    sub_papers = [row[0] for row in sub_papers]

    if sub_papers:
        return render_template(
            'pyq_qualifying_year.html',
            exam_type=exam_type,
            paper_type=paper_type,
            items=sub_papers,
            item_type='language'
        )
    else:
        years = db.session.query(UPSCPaper.year)\
            .filter_by(exam_type=exam_type, paper_type=paper_type)\
            .distinct().all()

        years = [row[0] for row in years]

        return render_template(
            'pyq_year.html',
            exam_type=exam_type,
            paper_type=paper_type,
            years=years
        )




@app.route('/pyq_year/<exam_type>/<paper_type>/<sub_paper_type>')
@login_required
def pyq_subpaper_year(exam_type, paper_type, sub_paper_type):

    years = db.session.query(UPSCPaper.year)\
        .filter_by(
            exam_type=exam_type,
            paper_type=paper_type,
            sub_paper_type=sub_paper_type
        ).distinct().all()

    years = [row[0] for row in years]

    return render_template(
        'pyq_qualifying_year.html',
        exam_type=exam_type,
        paper_type=paper_type,
        items=years,
        item_type='year',
        sub_paper_type=sub_paper_type
    )



@app.route('/pyq_final/<exam_type>/<paper_type>/<int:year>')
@app.route('/pyq_final/<exam_type>/<paper_type>/<sub_paper_type>/<int:year>')
@login_required
def pyq_final(exam_type, paper_type, year, sub_paper_type=None):

    query = UPSCPaper.query.filter_by(
        exam_type=exam_type,
        paper_type=paper_type,
        year=year
    )

    if sub_paper_type:
        query = query.filter_by(sub_paper_type=sub_paper_type)

    paper = query.first()

    if paper:
        return redirect(paper.pdf_link)

    return "PDF not found."




@app.route('/csat')
def csat_practice():
    with open('data/csat_data.json', 'r') as f:
        csat_data = json.load(f)
    return render_template('csat.html', csat_data=csat_data)


@app.route("/interview_index")
@login_required
def interview_index():
    
    return render_template("interview_index.html")

@app.route("/interview-overview")
@login_required
def interview_overview():
    return render_template("interview_overview.html")


@app.route("/interview_FAQs")
@login_required
def interview_FAQs():
    json_path = os.path.join(app.root_path, "data", "interview_faqs.json")

    with open(json_path, "r", encoding="utf-8") as file:
        faqs = json.load(file)

    return render_template("interview_FAQs.html", faqs=faqs)

@app.route('/interview_videos')
@login_required
def interview_videos():
    json_path = os.path.join('data', 'interview_videos.json') 
    with open(json_path, 'r') as f:
        videos = json.load(f)
    return render_template('interview_videos.html', videos=videos)

@app.route('/interview/daf')
@login_required
def interview_daf():

    with open('data/interview_DAF_videos.json', 'r', encoding='utf-8') as f:
        videos = json.load(f)

    pdf_folder_name = 'DAF_sample_pdfs'  
    pdf_folder = os.path.join(app.static_folder, pdf_folder_name)
    sample_pdfs = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]

    return render_template(
        'interview_DAF.html',
        videos=videos['DAF_Preparation'],
        sample_pdfs=sample_pdfs,
        pdf_folder_name=pdf_folder_name
    )


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import time

def fetch_updates():
    url = "https://www.upsc.gov.in/feeds/whats-new.xml"
    retries = 3
    for i in range(retries):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            print(f"RSS Fetch Attempt {i+1} Failed: {e}")
            time.sleep(2)
    else:
        return []  # after retries, return empty

    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")
    updates = []
    for item in items[:20]:
        updates.append({"title": item.title.text, "link": item.link.text})
    return updates


def categorize_updates(updates):
    categories = {
        'Results': [],
        'Admit Cards': [],
        'Exam Schedules': [],
        'Notifications': [],
        'Others': []
    }
    for update in updates:
        title = update['title'].lower()
        if 'result' in title:
            categories['Results'].append(update)
        elif 'admit card' in title or 'call letter' in title:
            categories['Admit Cards'].append(update)
        elif 'schedule' in title or 'timetable' in title:
            categories['Exam Schedules'].append(update)
        elif 'notification' in title:
            categories['Notifications'].append(update)
        else:
            categories['Others'].append(update)
    return categories

@app.route('/latest-updates')
@login_required
def latest_updates():
    updates = fetch_updates()
    categorized_updates = categorize_updates(updates)
    return render_template('latest_updates.html', updates=updates, categorized_updates=categorized_updates)

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "False") == "True")

