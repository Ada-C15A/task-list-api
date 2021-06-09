import requests
from dotenv import load_dotenv
import os
import datetime
from sqlalchemy import desc
from app import db
from app.models.task import Task
from flask import request, Blueprint, make_response, jsonify
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

load_dotenv()


@tasks_bp.route("/", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title)
        elif sort_query == "desc":
            tasks = Task.query.order_by(desc(Task.title))
        else:
            tasks = Task.query.all()

        tasks_response = []
        for task in tasks:
            if not task.completed_at:
                is_complete = False
            else:
                is_complete = True
            tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": is_complete
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
        if not request_body["completed_at"]:
            is_complete = False
        else:
            is_complete = True
        task_response = {"task":
                         {"id": new_task.task_id,
                          "title": new_task.title,
                          "description": new_task.description,
                          "is_complete": is_complete}
                         }
        return make_response(task_response), 201


@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return make_response(f"Task #{task_id} Not Found"), 404

    if request.method == "GET":
        if not task.completed_at:
            is_complete = False
        else:
            is_complete = True
        task_response = {"task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": is_complete
        }}
        return make_response(task_response), 200
    elif request.method == "PUT":
        form_data = request.get_json()
        if ("completed_at" not in form_data or
                form_data["completed_at"] == None):
            is_complete = False
        else:
            is_complete = True
        task.title = form_data["title"]
        task.description = form_data["description"]
        task.completed_at = form_data["completed_at"]
        db.session.commit()
        task_response = {"task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": is_complete
        }}
        return make_response(task_response), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        task_response = {
            "details": f"Task {task.task_id} \"{task.title}\" successfully deleted"
        }
        return make_response(task_response), 200


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_task_complete(task_id):
    task = Task.query.get(task_id)
    if not task:
        return make_response(f"Task #{task_id} Not Found"), 404

    task.completed_at = datetime.datetime.utcnow()
    db.session.commit()
    channel = "channel=task-notifications"
    text = f"text=Someone just completed the task {task.title}"

    path = f"https://slack.com/api/chat.postMessage?{channel}&{text}"

    SLACKBOT_AUTH = os.environ.get(
        "SLACKBOT_AUTH")

    requests.post(path, headers={'Authorization': f'Bearer {SLACKBOT_AUTH}'})

    task_response = {"task": {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": True
    }}
    return make_response(task_response), 200


@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_task_incomplete(task_id):
    # get current data, set the thing
    task = Task.query.get(task_id)
    if not task:
        return make_response(f"Task #{task_id} Not Found"), 404

    task.completed_at = None
    db.session.commit()

    task_response = {"task": {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": False
    }}
    return make_response(task_response), 200
