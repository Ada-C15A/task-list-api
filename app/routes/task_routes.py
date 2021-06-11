from app import db
from app.models.task import Task
from flask import Blueprint, request, make_response, jsonify
from datetime import datetime
import os
import requests

bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@bp.route("", strict_slashes=False, methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        sort_query = request.args.get("sort")
        
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title).all()
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc()).all()
        else:
            tasks = Task.query.all()
            
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
                        description=request_body["description"],
                        completed_at=request_body["completed_at"])
            
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

@bp.route("/<task_id>", strict_slashes=False, methods=["GET", "PUT", "DELETE"])
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
    
def post_to_slack(text):
    slack_token = os.environ.get("SLACK_POST_MESSAGE_API_TOKEN")
    slack_path = "https://slack.com/api/chat.postMessage"
    query_params ={
        "channel": "task-notifications",
        "text": text, 
    }
    headers = {"Authorization": f"Bearer {slack_token}"}
    requests.post(slack_path, params = query_params, headers = headers)   

@bp.route("/<task_id>/mark_complete", strict_slashes=False, methods=["PATCH"])
def mark_complete(task_id):
    task = Task.query.get(task_id)
    if not task:
        return make_response(f"Task {task_id} not found", 404)

    task.completed_at = datetime.utcnow()
    db.session.commit()
    
    slack_text = f"Someone just completed the task {task.title}"
    post_to_slack(slack_text)
    
    is_complete = True if task.completed_at else False
    return {
            "task": {"id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": is_complete}
        }

@bp.route("/<task_id>/mark_incomplete", strict_slashes=False, methods=["PATCH"])
def mark_incomplete(task_id):
    
    task = Task.query.get(task_id)
    if not task:
        return make_response(f"Task {task_id} not found", 404)

    task.completed_at = None
    db.session.commit()
    
    is_complete = True if task.completed_at else False
    return {
            "task": {"id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": is_complete}
        }
