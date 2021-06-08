from sqlalchemy import desc
from app import db
from app.models.task import Task
from flask import request, Blueprint, make_response, jsonify
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("/", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        # /tasks?sort=asc
        sort_query = request.args.get("sort")
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title)
        elif sort_query == "desc":
            tasks = Task.query.order_by(desc(Task.title))
        else:
            tasks = Task.query.all()

        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False
            })
        return make_response(jsonify(tasks_response)), 200

    elif request.method == "POST":
        request_body = request.get_json()
        keys = ['title', 'description', 'completed_at']
        for key in keys:
            if key not in request_body:
                task_response = {"details": "Invalid data"}
                return make_response(task_response), 400

        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"])

        db.session.add(new_task)
        db.session.commit()
        task_response = {"task":
                         {"id": new_task.task_id,
                          "title": new_task.title,
                          "description": new_task.description,
                          "is_complete": False}
                         }
        return make_response(task_response), 201

        # return make_response(f"task {new_task.task_id} successfully created", 201)


@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return make_response(f"Task #{task_id} Not Found"), 404

    if request.method == "GET":
        task_response = {"task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False
        }}
        return make_response(task_response), 200
    elif request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]
        task.completed_at = form_data["completed_at"]
        db.session.commit()
        task_response = {"task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False
        }}
        return make_response(task_response), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        task_response = {
            "details": f"Task {task.task_id} \"{task.title}\" successfully deleted"
        }
        return make_response(task_response), 200
