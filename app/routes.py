from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import request, Blueprint, make_response, jsonify, json
import datetime, requests, os

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")


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

def post_to_slack(slack_message):
    SLACK_TOKEN = os.environ.get('SLACK_ACCESS_TOKEN')
    slack_path = "https://slack.com/api/chat.postMessage"
    query_params ={
        'channel': 'task-notifications',
        'text': slack_message  
    }
    headers = {'Authorization': f"Bearer {SLACK_TOKEN}"}
    requests.post(slack_path, params=query_params, headers=headers)

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_task_completion(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("Not Found", 404)
    elif request.method == "PATCH":
        if bool(task.completed_at) == False:
            task.completed_at = datetime.datetime.now()
            slack_message =  f"Someone just completed the task {task.title}"
            post_to_slack(slack_message)
        return (
            { "task":{
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
        }}, 200
        )

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

@goals_bp.route("", methods=["GET","POST"])
def handle_goals():
    if request.method == "GET":
        goals = Goal.query.all()
        goals_response = [] 
        for goal in goals:   
            goals_response.append({
                "id": goal.goal_id,
                "title": goal.title,
            })
        return jsonify(goals_response)
    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return {"details": f"Invalid data"}, 400
        new_goal = Goal(
            title=request_body["title"]
            )
        db.session.add(new_goal)
        db.session.commit()

        return make_response( 
            {"goal": {
            "id": new_goal.goal_id,
            "title": new_goal.title
        }}, 201
        )

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)

    if goal is None:
        return make_response("Not Found", 404)
    elif request.method == "GET":
        return { "goal":{
            "id": goal.goal_id,
            "title": goal.title,
        }}
    elif request.method == "PUT":
        form_data = request.get_json()

        goal.title = form_data["title"]

        db.session.commit()

        return {
            "goal":{
            "id": goal.goal_id,
            "title": goal.title
        }}
    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return make_response({
            "details":f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"
        })