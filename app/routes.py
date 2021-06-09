from flask import request, Blueprint, make_response, jsonify
from app.models.task import Task
from app import db

tasks_bp = Blueprint("tasks", __name__, url_prefix="")

@tasks_bp.route("/tasks", strict_slashes=False, methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        tasks = Task.query.all()
        tasks_response = []
        for task in tasks:
            tasks_response.append(
                {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at or False
            })
        return jsonify(tasks_response)
    elif request.method == "POST":
        request_body = request.get_json()
        if 'title' not in request_body or 'description' not in request_body or 'completed_at' not in request_body:
            return make_response(jsonify({ "details": "Invalid data" }), 400)
        
        new_task = Task(title=request_body["title"],
                        description=request_body["description"]
                        )

        if "completed_at" in request_body:
            new_task.completed_at = request_body["completed_at"]

        db.session.add(new_task)
        db.session.commit()
        return make_response(jsonify({"task": { # todo - not really using jsonify?
            "id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": new_task.completed_at or False
        }
        }), 201)

@tasks_bp.route("/tasks/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_tast(task_id):
    task = Task.query.get(task_id)
    if not task:
        return make_response(f"Invalid data", 404)

    if request.method == "GET":
        return {
            "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at or False
            } 
        }
    elif request.method == "PUT":
        form_data = request.get_json()
        task.title = form_data["title"],
        task.description = form_data["description"]
        task.completed_at = form_data["completed_at"]

        db.session.commit()
        return make_response(jsonify({"task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at or False
        }}))
        
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify({'details': f'Task {task_id} "{task.title}" successfully deleted'})