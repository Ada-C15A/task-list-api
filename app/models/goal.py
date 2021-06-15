from flask import current_app
from sqlalchemy.orm import backref
from app import db
from sqlalchemy import ForeignKey, update
from sqlalchemy.orm import relationship


class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    task_ids = db.relationship('Task', backref='goal', lazy=True)