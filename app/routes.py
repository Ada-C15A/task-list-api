from app import db
from app.models.task import Task
from flask import request, Blueprint, make_response, jsonify


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    if request.method == "GET":
        title_query = request.args.get("title")
        if title_query:
            tasks = Task.query.filter(Task.title.ilike(f'%{title_query}%'))
        else:
            sort = request.args.get("sort")
            if not sort:
                tasks = Task.query.all()
            elif sort == "asc":
                tasks = Task.query.order_by(Task.title.asc()).all()
            elif sort == "desc":
                tasks = Task.query.order_by(Task.title.desc()).all()
            else:
                tasks = Task.query.all()
            
        tasks_response = []
        for task in tasks:
            tasks_response.append({
                "description": task.description,
                "is_complete": bool(task.completed_at),
                "id": task.task_id,
                "title": task.title,
            })
        return jsonify(tasks_response)
    
    elif request.method == "POST":
        request_body = request.get_json()
        title = request_body.get("title")
        description = request_body.get("description")
        if not title or not description or "completed_at" not in request_body:
            return jsonify({"details": "Invalid data"}), 400 
        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"])

        db.session.add(new_task)
        db.session.commit()
        commited_task = {"task":
            {"id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": bool(new_task.completed_at)}}
        
    return jsonify(commited_task), 201

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if request.method == "GET":
        if task == None:
            return make_response("No matching task found", 404)
        if request.method == "GET":
            selected_task = {"task":
            {"task_id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete
            }
            }
        return selected_task
    elif request.method == "PUT":
        form_data = request.get_json()
        
        task.title = form_data["title"]
        task.description = form_data["description"]
        task.completed_at = form_data["completed_at"]
        
        db.session.commit()
        
        commited_task = {"task": 
                        {"id": task.task_id,
                        "title": task.title,
                        "description": task.description,
                        "is_completed": bool(task.completed_at)
                    }
                    }
        return jsonify(commited_task), 200
    
    elif request.method == "DELETE":
        if task == None:
            return make_response("Task does not exist", 404)
        
        db.session.delete(task)
        db.session.commit()
        return jsonify(
        {f"details": 'Task 1 "Go on my daily walk 🏞" successfully deleted'}
    )
# @tasks_bp.route("/tasks?sort=<sort_method>", methods=["GET"])        
# def get_tasks_sorted(sort_method):
#     if sort_method == "asc":
#         tasks = Task.query.get.order_by(Task.title.asc()).all()
#     elif sort_method == "desc":
#         tasks = Task.query.get.order_by(Task.title.desc()).all()
#     tasks_response = []
    
#     for task in tasks:
#         print(f"Task: {task.title}")
#         tasks_response.append({
#             "description": task.description,
#             "is_complete": bool(task.completed_at),
#             "id": task.task_id, 
#             "title": task.title,
#         })
#     return make_response(tasks_response), 200     