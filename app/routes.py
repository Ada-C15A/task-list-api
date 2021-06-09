from app import db
from app.models.task import Task
from flask import request, Blueprint, make_response, jsonify

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    if request.method == "GET":
        tasks = Task.query.all()
        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "description": task.description,
                "is_complete": task.is_complete,
                "id": task.task_id,
                "title": task.title,
            })
        return jsonify(tasks_response)
    elif request.method == "POST":
        request_body = request.get_json()
        new_task = Task(title=request_body["title"],
                        description=request_body["description"])

        db.session.add(new_task)
        db.session.commit()
        
        return make_response(f"Task {new_task.title} successfully created", 201)

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    
    if request.method == "GET":
        if task == None:
            return make_response("No matching task found", 404)
        return { 
            "task": {
            "task_id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete
            }
        }
    elif request.method == "PUT":
        if task == None:
            return make_response("No matching task found", 404)
        form_data = request.get_json()
        
        task.name = form_data["title"]
        task.description = form_data["description"]
        task.completed_at = form_data["completed_at"]
        
        db.session.commit()
        
        return make_response(f"Task #{task.task_id} successfully updated")
    
    elif request.method == "DELETE":
        if task == None:
            return make_response("Task does not exist", 404)
        
        db.session.delete(task)
        db.session.commit()
        return make_response(f"Task #{task.task_id} successfully deleted.")