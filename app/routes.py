from flask import Blueprint, request, jsonify, make_response
from app import db
from app.models.task import Task
from datetime import datetime

task_list_api_bp = Blueprint("task_list_api", __name__)


@task_list_api_bp.route("/", methods=["GET", "POST"])
def tasks():
    if request.method == "GET":
        tasks = Task.query.all()
        tasks_response = []

        for task in tasks:
            tasks_response.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed_at": task.completed_at
            })
        return jsonify(tasks_response, 200)

    elif request.method == "POST":
        request_body = request.get_json(force=True)

        if 'title' not in request_body or 'description' not in request_body or 'completed_at' not in request_body:
            return {"details": "Invalid data"}, 400
        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"])
        db.session.add(new_task)
        db.session.commit()

        return {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": False
        }, 201


@task_list_api_bp.route("/<task_id>", methods=["GET", "DELETE", "PUT"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    print(task_id)
    if task is None:
        return make_response("{task_id} doesnt exist", 404)

    if request.method == "GET":
        is_complete = True if task.completed_at else False
        return {
            "task": {"id": task.id,
                     "title": task.title,
                     "description": task.description,
                     "is_complete": is_complete}
        }
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return make_response(f"Task #{task.id} deleted sucessfully")
    elif request.method == "PUT":
        form_data = request.get_json()
        task.title = form_data["title"]
        task.description = form_data["description"]
        completed_at = form_data["completed_at"]

        db.session.commit()

        return {
            "task": {
                "id": 1,
                "title": "Updated Task Title",
                "description": "Updated Test Description",
                "is_complete": false
            }
        }, 200
