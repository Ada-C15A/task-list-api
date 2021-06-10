from flask import Blueprint, request, make_response, jsonify
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET"])
def handle_tasks():
    if request.method == "GET":
        tasks = Task.query.all()
        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "task_id": task.task_id,
                "title": task.title,
                "description": task.description,
                "completed_at": task.completed_at
            })
        return jsonify(tasks_response)
    