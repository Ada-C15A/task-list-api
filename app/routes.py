from flask import Blueprint
from app.models.task import Task
from app import db
from flask import request, Blueprint, make_response, jsonify

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("", methods=["POST","GET"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return {"details": f"Invalid data"}, 400
        
        new_task = Task(
            id=request_body["id"],
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()
        
        if new_task.completed_at == None:
            new_task.completed_at = False
        else:
            new_task.completed_at = True
        return jsonify(new_task), 200

    elif request.method == "GET":
        tasks = Task.query.all()
        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "completed_at": bool(task.completed_at)
            })
        return jsonify(tasks), 200


@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response("", 404)

    if request.method == "GET":
        return { "task":{
          "id": task.task_id,
          "title": task.title,
          "description": task.description,
          "is_complete": bool(task.completed_at)
          }
        }, 200

    elif request.method == "PUT":
        form_data = request.get_json()
        task.title = form_data["title"]
        task.description = form_data["description"]
        db.session.commit()
        return make_response(f"Task #{task.task_id} has been updated.", 201)

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()

        return {"details":f"Task {task.task_id} \"{task.title}\" successfully deleted"}