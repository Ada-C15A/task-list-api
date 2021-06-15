from flask import current_app
from app import db

class Goal(db.Model):
    goal_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", backref="task", lazy=True)

    def goal_to_json(self):
        return {
            "id": self.goal_id,
            "title": self.title
                }