from flask import Blueprint
from app.models.task import Task
from app import db
from flask import request, Blueprint, make_response, jsonify

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks") #/tasks?

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "POST": 
        request_body = request.get_json()
        title = request_body.get("title")
        description = request_body.get("description")

        if not title or not description or "completed_at" not in request_body:
            return make_response(jsonify({"details": "Invalid data"}), 400)

        new_task = Task(
                    title=request_body["title"],
                    description=request_body["description"],
                    completed_at=request_body["completed_at"])

        if new_task.completed_at == None:
            completed_at = False
        else:
            completed_at = True

        db.session.add(new_task)
        db.session.commit()

        return make_response({
            "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": completed_at
            }}, 201)

    elif request.method == "GET":
        url_title = request.args.get("title")
        if url_title:
            tasks = Task.query.filter_by(title=url_title)
        else: 
            tasks = Task.query.order_by(Task.title).all()

        sort = request.args.get("sort")
        if not sort:
            tasks = Task.query.all()
        elif sort == "asc":
            tasks = Task.query.order_by(Task.title.asc()).all()
        elif sort == "desc":
            tasks = Task.query.order_by(Task.title.desc()).all()
        else:
            tasks = Task.query.all()
            
        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)
            })
        return jsonify(tasks_response)

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])    
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("No matching task found", 404)

    if request.method == "GET":
        selected_task = {"task": 
            {"id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
        }}
        return jsonify(selected_task), 200

    elif request.method == "PUT": 
        request_body = request.get_json()

        task.title = request_body["title"]
        task.description = request_body["description"]
        task.completed_at = request_body["completed_at"]

        updated_task = {"task": 
            {"id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
        }}
        db.session.add(task)
        db.session.commit()
        return make_response(jsonify(updated_task)), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        task_response_body = {
            "details":
                f'Task {task.task_id} \"{task.title}\" successfully deleted'
            }
        return jsonify(task_response_body), 200

# https://github.com/OhCloud/task-list-api
# https://github.com/Ada-C15A/task-list-api/pull/3