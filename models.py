# models.py
""" Database models for blog app """
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        """Create hashed password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password"""
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    """Post model"""
    id = db.Column(db.Integer, primary_key=True)
    header = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='posts')
    