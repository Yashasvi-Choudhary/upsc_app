from flask import Flask, flash, render_template, request, redirect, url_for , jsonify , send_from_directory, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import requests , json 
import openai
import os
import io
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:harharmahadev@localhost/upsc_app'


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
   

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = True if 'remember' in request.form else False

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password!", "danger")
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']


        user = User.query.filter_by(email=email).first()
        if user:
            flash("An account with this email already exists! Please log in.", "warning")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')






# API_KEY = "ad6c63ddf55d42f5b0cb911852e4ea15"  # Replace with your API Key
# NEWS_URL =" https://newsapi.org/v2/top-headlines?country=in&category=general&apiKey=ad6c63ddf55d42f5b0cb911852e4ea15"


# NEWS_API_KEY = 'ca5b3974b4fe4f05a29125b28554c1f3'  # Replace with your NewsAPI key

NEWS_API_KEY = os.environ.get('NEWS_API_KEY', 'ca5b3974b4fe4f05a29125b28554c1f3')
NEWS_API_BASE_URL = "https://newsapi.org/v2/"

# Create a directory for static files if it doesn't exist
if not os.path.exists('static'):
    os.makedirs('static')

# Updated categories with Sports included
CATEGORIES = {
    "india": "India",
    "world": "World",
    "politics": "Politics",
    "business": "Business", 
    "technology": "Technology",
    "sports": "Sports",  # Added Sports category
    "environment": "Environment",
    "science": "Science",
    "health": "Health",
    "education": "Education",
    "defence": "Defence"
}


@app.route('/current_affairs')  # Add this route to handle /current_affairs
def current_affairs():
    return render_template('current_affairs.html', categories=CATEGORIES)

@app.route('/news/<category>')
def get_news_by_category(category):
    # Get today's date and date from 7 days ago
    today = datetime.now().strftime('%Y-%m-%d')
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Default to 'india' if invalid category
    if category not in CATEGORIES and category != 'top':
        category = 'india'
    
    if category == 'top':
        # Get top headlines
        endpoint = f"{NEWS_API_BASE_URL}top-headlines"
        params = {
            'country': 'in',
            'apiKey': NEWS_API_KEY,
            'pageSize': 10
        }
    else:
        # Use different queries based on the category for better differentiation
        endpoint = f"{NEWS_API_BASE_URL}everything"
        
        # Category-specific query parameters
        if category == 'india':
            query = "India AND (government OR ministry OR policy OR national) NOT (Pakistan OR China OR World)"
        elif category == 'world':
            query = "World AND (international OR global OR foreign) NOT India"
        elif category == 'sports':
            query = "sports AND (cricket OR olympics OR football OR athletics) AND India"
        else:
            query = f"{category} AND (india OR upsc OR government OR ministry OR policy)"
        
        params = {
            'q': query,
            'from': week_ago,
            'to': today,
            'language': 'en',
            'sortBy': 'publishedAt',
            'apiKey': NEWS_API_KEY,
            'pageSize': 20
        }
    
    try:
        response = requests.get(endpoint, params=params)
        news_data = response.json()
        
        if response.status_code == 200:
            return jsonify(news_data)
        else:
            return jsonify({"error": "Failed to fetch news", "details": news_data}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search')
def search_news():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    
    # Get today's date and date from 30 days ago
    today = datetime.now().strftime('%Y-%m-%d')
    month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    endpoint = f"{NEWS_API_BASE_URL}everything"
    params = {
        'q': f"{query} AND (india OR upsc OR government OR policy)",
        'from': month_ago,
        'to': today,
        'language': 'en',
        'sortBy': 'relevancy',
        'apiKey': NEWS_API_KEY,
        'pageSize': 20
    }
    
    try:
        response = requests.get(endpoint, params=params)
        news_data = response.json()
        
        if response.status_code == 200:
            return jsonify(news_data)
        else:
            return jsonify({"error": "Failed to fetch news", "details": news_data}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Generate placeholder image
@app.route('/api/placeholder/<int:width>/<int:height>')
def placeholder_image(width, height):
    # Limit dimensions for security
    width = min(width, 1200)
    height = min(height, 1200)
    
    # Create a gray image with the specified dimensions
    img = Image.new('RGB', (width, height), color=(200, 200, 200))
    d = ImageDraw.Draw(img)
    
    # Add text with dimensions
    try:
        # Try to use a font if available
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        # Fall back to default font
        font = ImageFont.load_default()
    
    text = f"Placeholder {width}x{height}"
    text_width, text_height = d.textsize(text, font=font) if hasattr(d, 'textsize') else (100, 20)
    
    # Position text in the center
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    # Draw text and border
    d.text((text_x, text_y), text, fill=(100, 100, 100), font=font)
    d.rectangle([(0, 0), (width-1, height-1)], outline=(150, 150, 150))
    
    # Save to a bytes buffer
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    
    return Response(buf.getvalue(), mimetype='image/jpeg')

# Add a route to serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)




# Load data from JSON file
with open('data/static_gk_topics.json', 'r') as file:
    topics = json.load(file)


@app.route('/static_gk')
@login_required
def static_gk():
    return render_template("static_gk.html")

@app.route('/gk_topics')
def show_topics():
    return render_template('gk_topics.html', topics=topics)




@app.route('/syllabus')
@login_required
def syllabus():
    return render_template("syllabus.html")





# Load PDF links from JSON file
with open('data/pyq_links.json', 'r') as f:
    pdf_links = json.load(f)


@app.route('/previous_papers')
@login_required
def previous_papers():
    return render_template("previous_papers.html")

# Year-wise categories
@app.route('/pyq_years')
def years():
    years = list(pdf_links.keys())
    return render_template('pyq_years.html', years=years)

# Exam types for a specific year
@app.route('/pyq_examType/<year>')
def exams(year):
    exams = list(pdf_links.get(year, {}).keys())
    return render_template('pyq_examType.html', year=year, exams=exams)

# Papers for a specific year and exam type
@app.route('/pyq_papers/<year>/<exam>')
def papers(year, exam):
    papers = pdf_links.get(year, {}).get(exam, {})
    return render_template('pyq_papers.html', year=year, exam=exam, papers=papers)






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







# NCERT Home page
@app.route('/ncert_index')
@login_required
def ncert_index():
    return render_template("ncert_index.html")

# Load the JSON file
with open('books.json', 'r') as f:
    books_data = json.load(f)
    
# Classes page
@app.route('/classes')
def classes():
    return render_template('classes.html')

# Subjects page
@app.route('/subjects/<int:class_num>')
def subjects(class_num):
    class_key = f"class{class_num}"
    if class_key in books_data:
        subjects = books_data[class_key].keys()
        return render_template('subjects.html', class_num=class_num, subjects=subjects)
    else:
        return "Class not found", 404

# Chapters page
@app.route('/chapters/<int:class_num>/<string:subject>')
def chapters(class_num, subject):
    class_key = f"class{class_num}"
    if class_key in books_data and subject in books_data[class_key]:
        chapters = books_data[class_key][subject]
        return render_template('chapters.html', class_num=class_num, subject=subject, chapters=chapters)
    else:
        return "Subject or class not found", 404


# Redirect to external PDF link
@app.route('/download/<int:class_num>/<string:subject>/<string:chapter>')
def download(class_num, subject, chapter):
    class_key = f"class{class_num}"
    if class_key in books_data and subject in books_data[class_key] and chapter in books_data[class_key][subject]:
        pdf_url = books_data[class_key][subject][chapter]
        return redirect(pdf_url)
    else:
        return "Chapter not found", 404


if __name__ == '__main__':
 with app.app_context():
    db.create_all()  # Run this once to create the database
    app.run(debug=True)