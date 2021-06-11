from flask import Blueprint, request, make_response, jsonify
from app.models.task import Task
from app import db

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        tasks = Task.query.all()
        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "task_id": task.task_id,
                "title": task.title,
                "description": task.description,
                "completed_at": task.completed_at
            })
        return jsonify(tasks_response)
    elif request.method == "POST":
        # check for missing items
        request_body = request.get_json()

        if "title" not in request_body or "description" not in request_body or  "completed_at" not in request_body:
            return make_response({"details": "Invalid data"},400)
        
        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"])
        db.session.add(new_task)
        db.session.commit()

        return make_response({
            "task":{
                "id":new_task.task_id,
                "title":new_task.title,
                "description":new_task.description,
                "is_complete": False if not new_task.completed_at else True}}, 201)


    # elif request.method == "PUT":
    #     form_data = request.get_json()

    #     Task.title = form_data["title"]
    #     Task.description = form_data["description"]
    #     Task.completed_at = form_data["completed_at"]
    #     db.session.commit()
    #     return make_response(f"Task {Task.task_id} successfully updated", 200)
