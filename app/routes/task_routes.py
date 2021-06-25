from app import db
from app.models.task import Task
from .route_helpers import *
from flask import Blueprint, request, make_response, jsonify
import datetime

bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@bp.route("", methods=["GET"])
def get_tasks():
    sort_query = request.args.get("sort")
    search_title_query = request.args.get("search_title")
    if sort_query:
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title).all()
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc()).all()
        else:
            return make_response(f"{sort_query} is not a valid sort parameter. Please use sort=asc or sort=desc.", 400)
    elif search_title_query:
        tasks = Task.query.filter_by(title=search_title_query).all()
    else:
        tasks = Task.query.all()
        
    return jsonify([task.to_json() for task in tasks])

@bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    for attribute in {"title", "description", "completed_at"}:
        if attribute not in request_body:
            return make_response({"details": "Invalid data"}, 400)   

    if request_body["completed_at"]:
        date_time_response = validate_datetime(request_body["completed_at"])
        if type(date_time_response) != datetime.datetime:
            return date_time_response

    new_task = Task(title=request_body["title"],
                    description=request_body["description"])
    
    new_task.completed_at = date_time_response.strftime("%m/%d/%Y, %H:%M:%S") if request_body["completed_at"] else None
        
    db.session.add(new_task)
    db.session.commit()
    
    return make_response({"task": new_task.to_json()}, 201)

@bp.route("/<task_id>", methods=["GET"])
def get_task(task_id):
    task_response = validate_item("task", task_id)
    if type(task_response) != Task:
        return task_response

    return {"task": task_response.to_json()}

@bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task_response = validate_item("task", task_id)
    if type(task_response) != Task:
        return task_response    

    form_data = request.get_json()
    for attribute in {"title", "description"}:
        if attribute not in form_data:
            return make_response({"details": "Invalid data"}, 400)   
    
    if form_data["completed_at"]:
        date_time_response = validate_datetime(form_data["completed_at"])
        if type(date_time_response) != datetime.datetime:
            return date_time_response
    
    task_response.title = form_data["title"],
    task_response.description = form_data["description"]
    task_response.completed_at = date_time_response.strftime("%m/%d/%Y, %H:%M:%S") if form_data["completed_at"] else None
    
    db.session.commit()
    
    return {"task": task_response.to_json()}

@bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task_response = validate_item("task", task_id)
    if type(task_response) != Task:
        return task_response   

    db.session.delete(task_response)
    db.session.commit()
    return make_response(
        {"details": 
            f"Task {task_response.id} \"{task_response.title}\" successfully deleted"
        }
    )

@bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task_response = validate_item("task", task_id)
    if type(task_response) != Task:
        return task_response   

    task_response.completed_at = datetime.datetime.utcnow()
    db.session.commit()
    
    slack_text = f"Someone just completed the task {task_response.title}"
    post_to_slack(slack_text)
    return {"task": task_response.to_json()}

@bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task_response = validate_item("task", task_id)
    if type(task_response) != Task:
        return task_response   
    
    task_response.completed_at = None
    db.session.commit()
    return {"task": task_response.to_json()}