from flask import Blueprint, request, make_response, jsonify
from sqlalchemy.orm import query
from sqlalchemy import desc
from app.models.task import Task
from app import db

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

# Get all tasks and create a task
@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        sort_order = request.args.get("sort")
        if sort_order == "asc":
            tasks = Task.query.order_by(Task.title)
        elif sort_order == "desc":
            tasks = Task.query.order_by(desc(Task.title))
        else:
            tasks = Task.query.all()

        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if not task.completed_at else True,
            })
        return jsonify(tasks_response)
    elif request.method == "POST":
        request_body = request.get_json()

        # check for missing items
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

# Get one task and 
@tasks_bp.route("/<task_id>", methods=["GET","PUT","DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("Task not found", 404)
    
    if request.method == "GET":
        return {"task":{
                "id":task.task_id,
                "title":task.title,
                "description":task.description,
                "is_complete": False if not task.completed_at else True
        }}

    elif request.method == "PUT":
        form_data = request.get_json()
        # check for missing items
        if "title" not in form_data or "description" not in form_data or  "completed_at" not in form_data:
            return make_response({"details": "Invalid data"},400)

        task.title = form_data["title"]
        task.description = form_data["description"]
        task.completed_at = form_data["completed_at"]
        db.session.commit()
        return make_response({
            "task":{
                "id":task.task_id,
                "title":task.title,
                "description":task.description,
                "is_complete": False if not task.completed_at else True}}, 200)

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return make_response({"details": f'Task {task.task_id} "{task.title}" successfully deleted'})
