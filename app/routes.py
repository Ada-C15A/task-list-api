from app import db
from app.models.task import Task
from flask import request, Blueprint, make_response, jsonify, json
import datetime

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("", methods=["GET","POST"])
def handle_tasks():
    if request.method == "GET":
        task_query = request.args.get("sort")
        if task_query == "asc":
            tasks = Task.query.order_by(Task.title)
        elif task_query == "desc":
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
    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return {"details": f"Invalid data"}, 400
        # if request_body["completed_at"] is None:
        #     request_body["completed_at"] = false
        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"]
                        )
        db.session.add(new_task)
        db.session.commit()

        return make_response( 
            {"task": {
            "id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": bool(new_task.completed_at)
        }}, 201)

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response("Not Found", 404)
    elif request.method == "GET":
        return { "task":{
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
        }}
    elif request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]
        task.completed_at = form_data["completed_at"]

        db.session.commit()

        return {
            "task":{
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
        }}
    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return make_response({
            "details":f"Task {task.task_id} \"{task.title}\" successfully deleted"
        })

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_task_completion(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("Not Found", 404)
    elif request.method == "PATCH":
        if bool(task.completed_at) == False:
            task.completed_at = datetime.datetime.now()
        return ({ "task":{
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
        }}, 200)

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_task_not_completion(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("Not Found", 404)
    elif request.method == "PATCH":
        task.completed_at = None
        return ({ "task":{
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False
        }}, 200)

