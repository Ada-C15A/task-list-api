from app import db
from datetime import datetime
from flask import Blueprint
from flask import request
from flask import jsonify
from .models.task import Task
# from .models.goal import Goal
from flask import make_response

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
        if request.method == "GET":
            tasks = Task.query.all()
            tasks_response = []
            for task in tasks:
                tasks_response.append({
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": True if task.completed_at else False
                })
            sort_by_title = request.args.get("sort")
            if sort_by_title:
                if sort_by_title == "asc":
                    tasks_response = sorted(tasks_response, key = lambda i: i['title'])
                if sort_by_title == "desc":
                    tasks_response = sorted(tasks_response, key = lambda i: i['title'],reverse=True)
            return jsonify(tasks_response), 200

        elif request.method == "POST":
            request_body = request.get_json()
            if 'title' not in request_body or 'description' not in request_body or 'completed_at' not in request_body:
                return {"details": "Invalid data"}, 400
            new_task = Task(title=request_body["title"],
                                description=request_body["description"],
                                completed_at=request_body["completed_at"])


            db.session.add(new_task)
            db.session.commit()

        return {
            "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": True if new_task.completed_at else False
            }
        }, 201

@tasks_bp.route("/<task_id>", methods=["GET", "DELETE", "PUT"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    if request.method == "GET":
        return {
            "task":{
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": True if task.completed_at else False
            }
        }
    elif request.method == "DELETE":
        message = {"details": f"Task {task.task_id} \"{task.title}\" successfully deleted"}
        db.session.delete(task)
        db.session.commit()
        return make_response(message)
    elif request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]
        task.completed_at = form_data["completed_at"]

        db.session.commit()

        return make_response({
                "task": {
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": True if task.completed_at else False
                }
        })

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_task_complete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    task.completed_at = datetime.utcnow()
    db.session.commit()

    return make_response({
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": True
            }
    })

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_task_incomplete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    task.completed_at = None

    db.session.commit()

    return make_response({
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False
            }
    })