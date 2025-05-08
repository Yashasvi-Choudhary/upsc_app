from flask import Flask, flash, render_template, request, redirect, session, url_for , jsonify , Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests , json 
import openai
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from db_config import get_connection
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
import urllib.parse 
from flask import send_file
import calendar


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:harharmahadev@localhost/upsc_app'


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Home
@app.route('/')
def home():
    return render_template('index.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.", "warning")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)  # ✅ Auto-login after registration
        flash("Registration successful! Redirecting to dashboard.", "success")
        return redirect(url_for('dashboard'))

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for('dashboard'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Update profile
@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    new_username = request.form['new_username']
    new_email = request.form['new_email']
    current_user.username = new_username
    current_user.email = new_email
    db.session.commit()
    flash("Profile updated successfully!", "success")
    return redirect(url_for('dashboard'))

# Logout
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for('login'))






@app.route('/syllabus')
def syllabus_main():
    """Main syllabus page that asks users to select an exam type"""
    return render_template('syllabus_main.html')

@app.route('/syllabus/select_exam_type')
def syllabus_select_exam_type():
    """Page to select exam type (prelims or mains)"""
    return render_template('syllabus_select_exam_type.html')

@app.route('/syllabus/select_paper_type')
def syllabus_select_paper_type():
    """Page to select paper type based on the selected exam type"""
    exam_type = request.args.get('exam_type')
    if not exam_type:
        return redirect(url_for('syllabus_main'))
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get unique paper types available for this exam type
    query = """
        SELECT DISTINCT paper_type 
        FROM syllabus 
        WHERE exam_type = %s
    """
    cursor.execute(query, (exam_type,))
    paper_types = cursor.fetchall()
    conn.close()
    
    return render_template('syllabus_select_paper_type.html', 
                          exam_type=exam_type, 
                          paper_types=paper_types)

@app.route('/syllabus/show_syllabus')
def syllabus_show_syllabus():
    """Show available syllabi for the selected exam and paper type"""
    exam_type = request.args.get('exam_type')
    paper_type = request.args.get('paper_type')
    
    if not exam_type or not paper_type:
        return redirect(url_for('syllabus_main'))
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT id, exam_type, paper_type, year, link
        FROM syllabus
        WHERE exam_type = %s AND paper_type = %s
        ORDER BY year DESC
    """
    cursor.execute(query, (exam_type, paper_type))
    syllabi = cursor.fetchall()
    conn.close()
    
    return render_template('syllabus_show_syllabus.html', 
                          syllabi=syllabi, 
                          exam_type=exam_type, 
                          paper_type=paper_type)

@app.route('/syllabus/access/<int:syllabus_id>')
def access_syllabus(syllabus_id):
    """Access the syllabus PDF file - either download it or redirect to URL"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT link, exam_type, paper_type, year FROM syllabus WHERE id = %s"
    cursor.execute(query, (syllabus_id,))
    syllabus = cursor.fetchone()
    conn.close()
    
    if not syllabus or not syllabus['link']:
        return "Syllabus PDF not found", 404
    
    link = syllabus['link']
    
    # Check if it's a URL or a local file path
    parsed_url = urlparse(link)
    
    # If it's a web URL (starts with http or https)
    if parsed_url.scheme in ['http', 'https']:
        # Redirect to the URL
        return redirect(link)
    
    # If it's a local file path
    elif parsed_url.scheme == 'file':
        # Extract the file path
        file_path = urllib.parse.unquote(parsed_url.path)
        
        # Remove leading slash in Windows paths
        if os.name == 'nt' and file_path.startswith('/'):
            file_path = file_path[1:]
        
        # Check if file exists
        if not os.path.exists(file_path):
            return "Local PDF file not found", 404
        
        # Create a descriptive filename for the download
        filename = secure_filename(f"{syllabus['exam_type']}_{syllabus['paper_type']}_{syllabus['year']}.pdf")
        
        # Serve the file
        return send_file(file_path,
                        as_attachment=True,
                        download_name=filename,
                        mimetype='application/pdf')
    
    # If it's neither a URL nor a file path
    else:
        return "Invalid syllabus link format", 400



# API_KEY = "ad6c63ddf55d42f5b0cb911852e4ea15"  # Replace with your API Key
# NEWS_URL =" https://newsapi.org/v2/top-headlines?country=in&category=general&apiKey=ad6c63ddf55d42f5b0cb911852e4ea15"


# NEWS_API_KEY = 'ca5b3974b4fe4f05a29125b28554c1f3'  # Replace with your NewsAPI key


# ✅ Direct API key assignment (instead of os.getenv)
# NEWS_API_KEY = '231273fc510f4c319ee8e064eeefd15e'
# NEWS_API_URL = 'https://newsapi.org/v2/top-headlines'


# News API Configuration
NEWS_API_KEY = '231273fc510f4c319ee8e064eeefd15e'
NEWS_API_URL = 'https://newsapi.org/v2/everything'

# Categories for navigation
CATEGORIES = ['business', 'technology', 'sports', 'health', 'science', 'entertainment', 'politics']



# Helper function to get current date ranges for compilations
def get_date_ranges():
    today = datetime.now()
    
    # Weekly (last 7 days)
    start_of_week = today - timedelta(days=7)
    
    # Monthly (current month)
    current_month = today.month
    current_year = today.year
    month_name = calendar.month_name[current_month]
    
    # Format dates for display
    start_date = start_of_week.strftime('%d %b, %Y')
    end_date = today.strftime('%d %b, %Y')
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'month_name': month_name,
        'year': current_year
    }

# Helper function to fetch news
def get_news(category=None, query=None):
    # For top headlines (homepage and categories)
    if not query and (not category or category == 'all'):
        NEWS_API_ENDPOINT = f'{NEWS_API_URL}top-headlines'
        params = {
            'country': 'in',
            'apiKey': NEWS_API_KEY,
            'pageSize': 20
        }
    # For category-specific headlines
    elif not query and category != 'all':
        NEWS_API_ENDPOINT = f'{NEWS_API_URL}top-headlines'
        params = {
            'country': 'in',
            'category': category,
            'apiKey': NEWS_API_KEY,
            'pageSize': 20
        }
    # For search or query based results
    else:
        NEWS_API_ENDPOINT = f'{NEWS_API_URL}everything'
        params = {
            'q': query if query else 'India',
            'language': 'en',
            'sortBy': 'publishedAt',
            'apiKey': NEWS_API_KEY,
            'pageSize': 20
        }
    
    try:
        response = requests.get(NEWS_API_ENDPOINT, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return {"status": "error", "articles": []}

# Helper function to get news for compilation
def get_compilation_news(period='weekly'):
    compilation_data = {category: [] for category in CATEGORIES}
    
    today = datetime.now()
    
    # Set date range based on period
    if period == 'weekly':
        from_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    elif period == 'monthly':
        from_date = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
    else:  # yearly
        from_date = datetime(today.year, 1, 1).strftime('%Y-%m-%d')
    
    to_date = today.strftime('%Y-%m-%d')
    
    # Fetch news for each category
    for category in CATEGORIES:
        NEWS_API_ENDPOINT = f'{NEWS_API_URL}everything'
        params = {
            'q': f'{category} AND (India OR UPSC OR IAS OR civil services)',
            'from': from_date,
            'to': to_date,
            'language': 'en',
            'sortBy': 'relevancy',
            'apiKey': NEWS_API_KEY,
            'pageSize': 10
        }
        
        try:
            response = requests.get(NEWS_API_ENDPOINT, params=params)
            response.raise_for_status()
            news_data = response.json()
            
            if news_data['status'] == 'ok':
                # Add additional information for UPSC context
                for article in news_data['articles']:
                    # Add key points (placeholder - in a real app you might generate these)
                    article['key_points'] = [
                        f"Important point related to {category}",
                        "Relevant UPSC context",
                        "Policy implications"
                    ]
                
                compilation_data[category] = news_data['articles']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching compilation news for {category}: {e}")
    
    return compilation_data

# ------------------ ROUTES ------------------



@app.route('/current-affairs')
def current_affairs():
    category = request.args.get('category', 'all')
    query = request.args.get('query')
    
    news_data = get_news(category, query)
    
    carousel_items = news_data.get('articles', [])[:5]
    card_items = news_data.get('articles', [])[5:] if len(news_data.get('articles', [])) > 5 else []
    
    bookmarks = session.get('bookmarks', [])
    
    return render_template('current_affairs.html',
                           carousel_items=carousel_items,
                           card_items=card_items,
                           categories=CATEGORIES,
                           active_category=category,
                           bookmarks=bookmarks)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    if query:
        return redirect(url_for('current_affairs', query=query))
    return redirect(url_for('current_affairs'))

@app.route('/bookmark', methods=['POST'])
def bookmark():
    article_data = request.json
    bookmarks = session.get('bookmarks', [])
    bookmarked_urls = [bookmark['url'] for bookmark in bookmarks]
    
    if article_data['url'] in bookmarked_urls:
        bookmarks = [b for b in bookmarks if b['url'] != article_data['url']]
        action = 'removed'
    else:
        article_data['bookmarked_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        bookmarks.append(article_data)
        action = 'added'
    
    session['bookmarks'] = bookmarks
    
    return jsonify({'status': 'success', 'action': action, 'bookmark_count': len(bookmarks)})

@app.route('/bookmarks')
def view_bookmarks():
    bookmarks = session.get('bookmarks', [])
    return render_template('bookmarks.html',
                           bookmarks=bookmarks,
                           categories=CATEGORIES)

@app.route('/clear-bookmarks', methods=['POST'])
def clear_bookmarks():
    session['bookmarks'] = []
    return jsonify({'status': 'success'})

@app.route('/current-affairs/compilation/<period>')
def CA_compilation(period):
    """Show weekly/monthly/yearly compilation page."""
    if period not in ['weekly', 'monthly', 'yearly']:
        period = 'weekly'
    
    # Get date ranges for display
    date_ranges = get_date_ranges()
    
    # Get compilation data
    compilation_data = get_compilation_news(period)
    
    return render_template('CA_compilation.html', 
                          period=period,
                          categories=CATEGORIES,
                          compilation_data=compilation_data,
                          **date_ranges)





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
    # Add more mappings as needed
}


@app.route('/static_gk')
def static_gk():
    topics_data = load_topics()
    
    # Transform data for template
    formatted_topics = []
    for category, items in topics_data.items():
        if items and len(items) > 0:
            icon = topic_icons.get(category, "fa-book")  # Default icon if not found
            formatted_topics.append({
                "name": category,
                "icon": icon,
                "link": items[0]["link"]
            })
    
    return render_template('static_gk.html', topics=formatted_topics)







@app.route('/syllabus')
@login_required
def syllabus():
    return render_template("syllabus.html")







with open("NCERTdata.json") as f:
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














JSON_DATA_PATH = 'PYQs_upsc.json' 

# Load data from JSON file
def load_pyq_data():
    with open(JSON_DATA_PATH, 'r') as file:
        return json.load(file)

@app.route('/pyq')
def pyq_examtype():
    """PYQ first page showing exam types (PRELIMS/MAINS)"""
    exam_types = list(load_pyq_data().keys())
    return render_template('pyq_examtype.html', exam_types=exam_types)

@app.route('/pyq/<exam_type>')
def pyq_papertype(exam_type):
    """Show paper types based on exam type selected"""
    data = load_pyq_data()
    if exam_type not in data:
        return redirect(url_for('pyq_examtype'))
    
    paper_types = list(data[exam_type].keys())
    return render_template('pyq_papertype.html', exam_type=exam_type, paper_types=paper_types)

@app.route('/pyq/<exam_type>/<paper_type>')
def pyq_year(exam_type, paper_type):
    """Show available years for the selected exam and paper type"""
    data = load_pyq_data()
    
    # For QUALIFYING PAPERS within MAINS, show the languages
    if exam_type == "MAINS" and paper_type == "QUALIFYING PAPERS":
        languages = list(data[exam_type][paper_type].keys())
        return render_template('pyq_year.html', 
                              exam_type=exam_type, 
                              paper_type=paper_type,
                              items=languages,
                              item_type="language")
    
    # Regular paper types - show years
    if exam_type in data and paper_type in data[exam_type]:
        years = list(data[exam_type][paper_type].keys())
        years.sort(reverse=True)  # Sort years in descending order
        return render_template('pyq_year.html', 
                              exam_type=exam_type, 
                              paper_type=paper_type,
                              items=years,
                              item_type="year")
    
    return redirect(url_for('pyq_papertype', exam_type=exam_type))

@app.route('/pyq/<exam_type>/<paper_type>/<item>')
def pyq_final(exam_type, paper_type, item):
    data = load_pyq_data()
    
    # For QUALIFYING PAPERS, item is a language, so show years
    if exam_type == "MAINS" and paper_type == "QUALIFYING PAPERS":
        if item in data[exam_type][paper_type]:
            years = list(data[exam_type][paper_type][item].keys())
            years.sort(reverse=True)
            return render_template('pyq_qualifying_year.html',
                                   exam_type=exam_type,
                                   paper_type=paper_type,
                                   items=years,       # <-- changed to 'items'
                                   item_type="year",   # <-- added item_type
                                   language=item)
        return redirect(url_for('pyq_year', exam_type=exam_type, paper_type=paper_type))
    
    # For regular papers, item is a year, so download
    if exam_type in data and paper_type in data[exam_type] and item in data[exam_type][paper_type]:
        pdf_url = data[exam_type][paper_type][item]
        return redirect(pdf_url)
    
    return "PDF not found", 404

@app.route('/pyq/<exam_type>/<paper_type>/<language>/<year>')
def download_qualifying_paper(exam_type, paper_type, language, year):
    """Download qualifying paper for specific language and year"""
    data = load_pyq_data()
    
    if (exam_type == "MAINS" and 
        paper_type == "QUALIFYING PAPERS" and
        language in data[exam_type][paper_type] and
        year in data[exam_type][paper_type][language]):
        
        pdf_url = data[exam_type][paper_type][language][year]
        return redirect(pdf_url)
    
    return "PDF not found", 404




# Ensure OpenAI API key is set
OPENAI_API_KEY = "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"
if openai:
    openai.api_key = OPENAI_API_KEY

@app.route('/generate_quiz')
def generate_quiz():
    return render_template('generate_quiz.html')

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    if not openai:
        return jsonify({"error": "OpenAI module not found. Please install openai using 'pip install openai'."}), 500
    
    data = request.json
    topic = data.get('topic')
    difficulty = data.get('difficulty')

    # Generate quiz question using OpenAI
    prompt = f"Generate a {difficulty} level multiple-choice question on {topic} with 4 options and the correct answer. Format as JSON: {{'question': '', 'options': [], 'correct_answer': ''}}"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}]
        )
        question_data = response['choices'][0]['message']['content']
        return jsonify(question_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    









# OpenAI API key
# openai.api_key = 'ca5b3974b4fe4f05a29125b28554c1f3'

csat_topics = [
    "logical-reasoning", "data-interpretation", "reading-comprehension",
    "maths-basics", "puzzle-solving", "syllogisms", "coding-decoding",
    "direction-sense", "blood-relations", "time-and-work"
]

# AI-based descriptive generator
def generate_descriptive_notes(topic):
    return {
        "intro": f"Understanding the core concepts of {topic.replace('-', ' ')} is crucial for CSAT.",
        "points": [
            f"Definition and scope of {topic.replace('-', ' ')}.",
            f"Basic techniques to solve {topic.replace('-', ' ')} problems.",
            f"Common pitfalls in {topic.replace('-', ' ')} questions.",
            f"Tips and tricks to improve speed and accuracy."
        ],
        "formulas": [
            f"{topic.title()} Formula #1: Example formula for {topic.replace('-', ' ')} problems.",
            f"{topic.title()} Formula #2: Example formula for {topic.replace('-', ' ')} problems."
        ]
    }

# AI-based MCQ generator
def generate_mcqs(topic):
    mcqs = []
    for i in range(10):
        options = [f"Option A{i}", f"Option B{i}", f"Option C{i}", f"Option D{i}"]
        answer = random.choice(options)
        mcqs.append({
            "question": f"What is a basic concept related to {topic.replace('-', ' ')} #{i+1}?",
            "options": options,
            "answer": answer
        })
    return mcqs

@app.route("/csat-practice")
def csat_practice():
    return render_template("csat_practice.html", topics=csat_topics)

@app.route("/csat-topic")
def csat_topic():
    topic = request.args.get("topic")
    return render_template("csat_topic_options.html", topic=topic)

@app.route("/csat-notes/<topic>")
def csat_notes(topic):
    data = generate_descriptive_notes(topic)
    return render_template("csat_notes.html", topic=topic, data=data)

@app.route("/csat-test/<topic>", methods=["GET", "POST"])
def csat_test(topic):
    if request.method == "POST":
        score = 0
        mcqs = session.get("mcqs", [])
        for i, q in enumerate(mcqs):
            user_ans = request.form.get(f"q{i}")
            if user_ans == q['answer']:
                score += 1
        return render_template("csat_result.html", score=score, total=len(mcqs), mcqs=mcqs)
    else:
        mcqs = generate_mcqs(topic)
        session['mcqs'] = mcqs
        return render_template("csat_test.html", topic=topic, mcqs=mcqs)








if __name__ == '__main__':
 with app.app_context():
    db.create_all()  # Run this once to create the database
    app.run(debug=True)