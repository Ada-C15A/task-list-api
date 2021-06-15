from flask import current_app
from app import db
# from app.models.goal import Goal

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.goal_id"), nullable=True)
    __tablename__ = "tasks" 

    def to_json(self):
        if self.completed_at:
            completed = True
        else:
            completed = False

        task_dict={
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": completed,
            "goal_id": self.goal_id # if the task belongs a goal add if not do not add
        }

        if self.goals_id:
            task_dict["goal_id"]= self.goals_id
        return task_dict