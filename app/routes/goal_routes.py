from app import db
from app.models.goal import Goal
from app.models.task import Task
from flask import Blueprint, request, make_response, jsonify

bp = Blueprint("goals", __name__, url_prefix="/goals")

@bp.route("", strict_slashes=False, methods=["GET", "POST"])
def handle_goals():
    if request.method == "GET":
        goals = Goal.query.all()
        goals_response = []
        for goal in goals:
            goals_response.append({
                "id": goal.id,
                "title": goal.title
            })
        return jsonify(goals_response)
    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return make_response({"details": "Invalid data"}, 400)   
        new_goal = Goal(title=request_body["title"])
            
        db.session.add(new_goal)
        db.session.commit()
        
        return make_response({"goal":
            {
                "id": new_goal.id,
                "title": new_goal.title
                }
        }           
                             , 201)

@bp.route("/<goal_id>", strict_slashes=False, methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response(f"Goal {goal_id} not found", 404)

    if request.method == "GET":
        return {
            "goal": {"id": goal.id,
                     "title": goal.title}
        }
    elif request.method == "PUT":
        form_data = request.get_json()
        goal.title = form_data["title"],

        db.session.commit()
        
        return make_response({
            "goal":{
                "id": goal.id,
                "title": goal.title
            }
        }           
        )
    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return make_response(
            {"details": 
                f"Goal {goal.id} \"{goal.title}\" successfully deleted"
            }
        )
        
@bp.route("/<goal_id>/tasks", strict_slashes=False, methods=["GET"])
def get_goal_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response(f"Goal {goal_id} not found", 404)
    tasks = goal.tasks
    tasks_details = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "goal_id": goal.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete() 
        }
        tasks_details.append(task_dict)
    return make_response(
        {
            "id": goal.id,
            "title": goal.title,
            "tasks": tasks_details
        })       
  





@bp.route("/<goal_id>/tasks", strict_slashes=False, methods=["POST"])
def add_goal_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return make_response(f"Goal {goal_id} not found", 404)
    
    request_body = request.get_json()   
    for id in request_body["task_ids"]:
        task = Task.query.get(id)
        goal.tasks.append(task)
            
        db.session.add(goal)
        db.session.commit()
        
    return make_response(
            {
                "id": goal.id,
                "task_ids": request_body["task_ids"]
                })       
