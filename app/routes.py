from flask import request, Blueprint, make_response, jsonify
from app.models.task import Task
from app import db
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", strict_slashes=False, methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        sort_method = request.args.get("sort")
        if sort_method == "asc":
            tasks = Task.query.order_by(Task.title.asc()).all() 
        elif sort_method == "desc":
            tasks = Task.query.order_by(Task.title.desc()).all() 
        else:
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
                        description=request_body["description"],
                        completed_at=request_body["completed_at"],
                        )

        if "completed_at" in request_body:
            new_task.completed_at = request_body["completed_at"]
            # set_task = True   - Todo: Why couldn't I just set it here? Shouldn't need to set task below

        set_task_status = True if new_task.completed_at else False

        db.session.add(new_task)
        db.session.commit()
        return make_response(jsonify({"task": { # todo - not really using jsonify?
            "id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": set_task_status
        }
        }), 201)

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
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

        set_task_status = True if task.completed_at else False
        
        return make_response(jsonify({"task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": set_task_status
        }}))
        
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify({'details': f'Task {task_id} "{task.title}" successfully deleted'})

@tasks_bp.route("/<task_id>/mark_complete", strict_slashes=False, methods=["PATCH"])
def mark_complete(task_id):
    task = Task.query.get(task_id)
    if not task:
        return make_response(f"Task {task_id} not found", 404)
        
    task.completed_at  = datetime.utcnow()
    db.session.commit()

    return make_response(jsonify({"task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": True
        }}))

@tasks_bp.route("/<task_id>/mark_incomplete", strict_slashes=False, methods=["PATCH"])
def mark_incomplete(task_id):
    task = Task.query.get(task_id)
    if not task:
        return make_response(f"Task {task_id} not found", 404)

    task.completed_at = None
    db.session.commit()

    return make_response(jsonify({
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False
        }
    }))


