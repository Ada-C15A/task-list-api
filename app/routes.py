from app import db
from flask import Blueprint, json
from sqlalchemy import asc, desc 
from app.models.task import Task
from flask import request, make_response, jsonify


task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

# return all tasks
@task_bp.route("/", methods=["GET", "POST"], strict_slashes = False)
def handle_tasks():
    if request.method == "GET":

        # tasks by asc and desc order
        sort_by_url = request.args.get("sort") # query parameters and replace the previous query
        if sort_by_url == "asc": # this is a list queried by title in asc order
            tasks = Task.query.order_by(Task.title.asc()).all() 
        elif sort_by_url == "desc":
            tasks = Task.query.order_by(Task.title.desc()).all() 
        else:
            tasks = Task.query.all()
        # end of the new code
    
        tasks_response = []
        for task in tasks:
            tasks_response.append(task.to_json())
            return jsonify(tasks_response), 200

#create a task with null completed at
    elif request.method == "POST":
            request_body = request.get_json()
            if "title" in request_body and "description" in request_body and "completed_at" in request_body:

                new_task = Task(title=request_body["title"],
                                description=request_body["description"], 
                                completed_at=request_body["completed_at"])

                db.session.add(new_task) # "adds model to the db"
                db.session.commit() # commits the action above               
                return {
                        "task": new_task.to_json()
                    }, 201
                
            return {"details": "Invalid data"}, 400

# return one task
@task_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"], strict_slashes = False)
def handle_task(task_id):
    task = Task.query.get(task_id)

    if request.method == "GET":
        if task is None:
            return make_response(f"Task #{task_id} not found"), 404
        return {
            "task": task.to_json()
        }, 200

    # Update a task
    elif request.method == "PUT":
        if task is None:
            return make_response(f"Task #{task_id} not found"), 404
        form_data = request.get_json()
        if "title" in form_data or "description" in form_data or "completed_at" in form_data:
            task.title = form_data["title"]
            task.description = form_data["description"]
            task.completed_at = form_data["completed_at"]

        db.session.commit()
        return {
                    "task": task.to_json()
                }, 200
                

    # Delete a task
    elif request.method == "DELETE":
        if not task:
            return "", 404
        db.session.delete(task)
        db.session.commit()
        return {
        "details": f"Task {task_id} \"{task.title}\" successfully deleted"
        }, 200
            


