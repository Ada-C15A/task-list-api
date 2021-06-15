from app import db
from app.models.goal import Goal
from app.models.task import Task
from .route_helpers import validate_item
from flask import Blueprint, request, make_response, jsonify

bp = Blueprint("goals", __name__, url_prefix="/goals")

@bp.route("", methods=["GET"])
def get_goals():
    goals = Goal.query.all()
    return jsonify([goal.to_json() for goal in goals])

@bp.route("", methods=["POST"])
def create_goal():   
    request_body = request.get_json()
    if "title" not in request_body:
        return make_response({"details": "Invalid data"}, 400)   
    new_goal = Goal(title=request_body["title"])
        
    db.session.add(new_goal)
    db.session.commit()
    
    return make_response({"goal": new_goal.to_json()}, 201)

@bp.route("/<goal_id>", methods=["GET"])
def get_goal(goal_id):
    goal_response = validate_item("goal", goal_id)
    if type(goal_response) != Goal:
        return goal_response 
    return {"goal": goal_response.to_json()}

@bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    goal_response = validate_item("goal", goal_id)
    if type(goal_response) != Goal:
        return goal_response    
   
    form_data = request.get_json()
    goal_response.title = form_data["title"],
    db.session.commit()
    return {"goal": goal_response.to_json()}

   
@bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal_response = validate_item("goal", goal_id)
    if type(goal_response) != Goal:
        return goal_response    
    
    db.session.delete(goal_response)
    db.session.commit()
    return make_response(
        {"details": 
            f"Goal {goal_response.id} \"{goal_response.title}\" successfully deleted"
        }
    )
        
@bp.route("/<goal_id>/tasks", methods=["GET"])
def get_goal_tasks(goal_id):
    goal_response = validate_item("goal", goal_id)
    if type(goal_response) != Goal:
        return goal_response  
    
    tasks = goal_response.tasks
    tasks_details = [task.to_json() for task in tasks]    
    return make_response(
        {
            "id": goal_response.id,
            "title": goal_response.title,
            "tasks": tasks_details
        })       
  
@bp.route("/<goal_id>/tasks", methods=["POST"])
def add_goal_tasks(goal_id):
    goal_response = validate_item("goal", goal_id)
    if type(goal_response) != Goal:
        return goal_response  
    
    request_body = request.get_json()   
    for id in request_body["task_ids"]:
        task = Task.query.get(id)
        goal_response.tasks.append(task)
            
        db.session.add(goal_response)
    db.session.commit()
        
    return make_response(
        {"id": goal_response.id,
        "task_ids": request_body["task_ids"]
        })       
