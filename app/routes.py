from app import db
from app.models.task import Task
from flask import Blueprint, request, make_response, jsonify

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", strict_slashes=False, methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        tasks = Task.query.order_by(Task.task_id).all()
        tasks_response = []
        for task in tasks:
            is_complete = True if task.completed_at else False
            tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": is_complete
            })
        return jsonify(tasks_response)
    elif request.method == "POST":
        request_body = request.get_json()
        for attribute in {"title", "description", "completed_at"}:
            if attribute not in request_body:
                return make_response({"details": "Invalid data"}, 400)   
        new_task = Task(title=request_body["title"],
                        description=request_body["description"])
        db.session.add(new_task)
        db.session.commit()
        
        is_complete = True if new_task.completed_at else False
        return make_response({"task":
            {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": is_complete
                }
        }           
                             , 201)

@tasks_bp.route("/<task_id>", strict_slashes=False, methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return make_response(f"Task {task_id} not found", 404)

    if request.method == "GET":
        is_complete = True if task.completed_at else False
        return {
            "task": {"id": task.task_id,
                     "title": task.title,
                    "description": task.description,
                    "is_complete": is_complete}
        }
    elif request.method == "PUT":
        form_data = request.get_json()
        task.title = form_data["title"],
        task.description = form_data["description"]

        db.session.commit()
        
        is_complete = True if task.completed_at else False
        return make_response({
            "task":{
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": is_complete
            }
        }           
        )
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return make_response(
            {"details": 
                f"Task {task.task_id} \"{task.title}\" successfully deleted"
            }
        )
    