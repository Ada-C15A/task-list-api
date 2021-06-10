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
            tasks = Task.query.all()
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
        new_task = Task(id = request_body["id"],
                        title=request_body["title"],
                        description=request_body["description"],
                        is_complete=request_body["completed_at"])

        db.session.add(new_task)
        db.session.commit()

        return make_response(f"Task {new_task.title} successfully created", 201)

@tasks_bp.route("/<tasks_id>", methods=["GET", "PUT", "DELETE"])
def handle_planet(tasks_id):
    task = Task.query.get(tasks_id)
    if task is None:
        return make_response("", 404)

    if request.method == "GET":
        selected_task = {"task":{
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)}
        }
        return selected_task
    elif request.method == "PUT":
        form_data = request.get_json()
        task.title = form_data["title"]
        task.description = form_data["description"]
        task.completed_at = form_data["completed_at"]
        db.session.commit()
        return make_response(f"Task #{task.id} successfully updated!!")
   
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return make_response(f'Task {task.id} "{task.description}"successfully deleted')
