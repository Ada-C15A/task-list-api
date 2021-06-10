from app import db
from app.models.task import Task
from flask import request, Blueprint, make_response, jsonify

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():        
    if request.method == "GET":
        title_from_url = request.args.get("title")
        if title_from_url:
            tasks = Task.query.filter_by(title=title_from_url)
        else:
            tasks = Task.query.order_by(Task.title).all()
        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)
            })
        return jsonify(tasks_response)

    elif request.method == "POST":
        request_body = request.get_json()
        title = request_body.get("title")
        description = request_body.get("description")

        if not title or not description or "completed_at" not in request_body:
            return jsonify({"details": "Invalid data"}), 400

        new_task = Task(title=title,
                        description=description,
                        completed_at=request_body["completed_at"])
        db.session.add(new_task)
        db.session.commit()
        commited_task = {"task":
            {"id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": bool(new_task.completed_at)
            }}
        
        return jsonify(commited_task), 201

@tasks_bp.route("/<tasks_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(tasks_id):
    task = Task.query.get_or_404(tasks_id)
    if request.method == "GET":
        selected_task = {"task":
            {"id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
            }}
        return jsonify(selected_task),200

    elif request.method == "PUT":
        request_body = request.get_json()
        task.title = request_body["title"]
        task.description = request_body["description"]
        task.completed_at = request_body["completed_at"]
        updated_task = {'task':{
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)
            }}
        db.session.commit()
        return jsonify(updated_task),200

   
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        task_response_body = {"details": f'Task {task.id} "{task.title}" successfully deleted'}
        return jsonify(task_response_body),200