from extensions import db
from flask_login import UserMixin
from datetime import datetime



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    session_token = db.Column(db.String(255), nullable=True)

class UPSCPaper(db.Model):
    __tablename__ = 'upsc_papers'
    id = db.Column(db.Integer, primary_key=True)
    exam_type = db.Column(db.String(50))
    paper_type = db.Column(db.String(100))
    sub_paper_type = db.Column(db.String(50))
    year = db.Column(db.Integer)
    pdf_link = db.Column(db.Text)




class Syllabus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_type = db.Column(db.String(100), nullable=False)
    paper_type = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 




class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow) 