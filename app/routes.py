
from app import db
from app.models.task import Task
from flask import request, Blueprint, make_response, jsonify
from sqlalchemy import asc, desc

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


def is_complete(completed_at):
  
    if completed_at is None:
        return False
    else:
        return True

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():

    if request.method == "GET":
        tasks = Task.query.all()
        title_query = request.args.get("sort")
        if title_query == "asc":
            tasks = Task.query.order_by(asc(Task.title))
        elif title_query == "desc":
            tasks = Task.query.order_by(desc(Task.title))
            
        tasks_response = []
        
        for task in tasks:
            if task.completed_at is None :
                 tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete" : False
            })
            else:
                tasks_response.append({
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "completed_at": task.completed_at,
                    "is_complete" : False
                })
        return jsonify(tasks_response), 200
      
    if request.method == "POST": 
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return make_response({
                "details": "Invalid data"
                }, 400)
        else:
            new_task = Task(title=request_body["title"], description=request_body["description"], completed_at=request_body["completed_at"])
            db.session.add(new_task)
            db.session.commit()
            return make_response(
                    { "task": {
                    "id": new_task.task_id,
                    "title": new_task.title,
                    "description": new_task.description,
                    "is_complete": is_complete(new_task.completed_at)
                    }}, 201)

@tasks_bp.route("/<task_id>", methods=["GET","PUT", "DELETE"])
def handle_tasks_id(task_id):
    task = Task.query.get(task_id)
    if task is None:
            return make_response("", 404)

    if request.method == "GET":
        if task is not None:
            return {"task":{
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": False    
        }}
    
    
    elif request.method == "PUT":
        data = request.get_json()
        
        task.title = data["title"]
        task.description = data["description"]
        task.completed_at = data["completed_at"]

        db.session.commit()
        
        data_response= {
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": is_complete(task.completed_at)
        }
    }
        return make_response(jsonify(data_response),200)
   

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        
        delete_id_response= f'Task {task.task_id} "{task.title}" successfully deleted'
        
        return make_response(jsonify({"details":delete_id_response}))



