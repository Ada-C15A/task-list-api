from app import db
from app.models.task import Task
from flask import request, Blueprint, make_response, jsonify

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        title = request_body.get("title")
        description = request_body.get("description")

        if not title or not description or "completed_at" not in request_body:
            return jsonify({"details": "Invalid data"}), 400

        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"])
        db.session.add(new_task)
        db.session.commit()
        db_task = {
            "task":
            {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": bool(new_task.completed_at)
            }
        }
        return db_task, 201
    
    elif request.method == "GET":
        tasks = Task.query.all()
        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                # "is_complete": task.completed_at==True
                "is_complete": bool(task.completed_at)
            })
        return jsonify(tasks_response)      

    db.session.add(new_task)
    db.session.commit()



    return make_response(f"Task {new_task.title} successfully created", 201)

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    if request.method == "GET":
        selected_task = {
            "task":
            {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                # "is_complete": task.completed_at==True
                "is_complete": bool(task.completed_at)
            }
        }
        return selected_task

    elif request.method == "PUT":
        request_body = request.get_json()

        task.title = request_body["title"]
        task.description = request_body["description"]
        task.completed_at = request_body["completed_at"]

        updated_task = {
            "task":
            {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)
            }
        }

        db.session.commit()
        return make_response(updated_task, 200)

    elif request.method == "DELETE":
        response = {
            "details":
            f'Task {task.task_id} "{task.title}" successfully deleted'
        }
        db.session.delete(task)
        db.session.commit()
        return make_response(response, 200)