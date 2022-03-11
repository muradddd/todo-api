from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    todos = db.relationship('Todo', backref="user")

    def __repr__(self) -> str:
        return 'User>>> {self.username}'


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=True)
    is_complete = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self) -> str:
        return 'Todo>>> {self.url}'
