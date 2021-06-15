from flask import current_app
from app import db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, update


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.VARCHAR(50))
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True, default=None)
    is_complete = db.Column(db.Boolean, default=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'))