from app import db
from app.models.goal import Goal
from flask import Blueprint, request, make_response, jsonify

bp = Blueprint("goals", __name__, url_prefix="/goals")

@bp.route("", strict_slashes=False, methods=["GET", "POST"])
def handle_goals():
    if request.method == "GET":
        goals = Goal.query.all()
        goals_response = []
        for goal in goals:
            goals_response.append({
                "id": goal.goal_id,
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
                "id": new_goal.goal_id,
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
            "goal": {"id": goal.goal_id,
                     "title": goal.title}
        }
    elif request.method == "PUT":
        form_data = request.get_json()
        goal.title = form_data["title"],

        db.session.commit()
        
        return make_response({
            "goal":{
                "id": goal.goal_id,
                "title": goal.title
            }
        }           
        )
    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return make_response(
            {"details": 
                f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"
            }
        )