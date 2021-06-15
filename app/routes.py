from flask.json import jsonify
from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import request, Blueprint, make_response, jsonify
from datetime import date, datetime
from dotenv import load_dotenv
import requests
import os

load_dotenv()
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint('goals', __name__, url_prefix="/goals")

@tasks_bp.route("", methods=["GET","POST"])
def handle_tasks():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return {
                "details": f"Invalid data"
            }, 400
        new_task = Task(
            title=request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"]
        )
        db.session.add(new_task)
        db.session.commit()
        if new_task.completed_at == None:
            completed_at = False
        else:
            completed_at = True
        return make_response({
            "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": completed_at
            }
        }, 201)

    elif request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query == "asc":
            tasks = Task.query.order_by(Task.title).all()
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc()).all()
        else:
            tasks = Task.query.all()

        tasks_response = []
        for task in tasks:
            if task.completed_at == None:
                completed_at = False
            else:
                completed_at = True
            tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": completed_at
            })
        return make_response(jsonify(tasks_response), 200)

@tasks_bp.route("/<task_id>", methods=["GET","PUT","DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    if request.method == "GET":
        if task.completed_at == None:
            completed_at = False
        else:
            completed_at = True

        if task.goal_id == None:
            return make_response({
                "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": completed_at
                }
            })
        else:
            # goal_id = task.goal_id
            return make_response({
                "task": {
                    "id": task.task_id,
                    "title": task.title,
                    "goal_id": task.goal_id,
                    "description": task.description,
                    "is_complete": completed_at
                }
            })

    elif request.method == "PUT":
        form_data = request.get_json()
        if ("completed_at" not in form_data or form_data["completed_at"] == None):
            is_complete = False
        else:
            is_complete = True
        task.title = form_data["title"]
        task.description = form_data["description"]
        task.completed_at = form_data["completed_at"]
        db.session.commit()
        response_task = {
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": is_complete
            }
        }
        return make_response(response_task, 200)

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        if task.completed_at == None:
            completed_at = False
        else:
            completed_at = True
        return make_response(
            {
            "details":
               f"Task {task.task_id} \"{task.title}\" successfully deleted"
            }
        )

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task = Task.query.get(task_id)

    if task == None:
        return  make_response(f"Task {task_id} not found", 404)

    task.completed_at = datetime.utcnow()
    db.session.commit()
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    slack_path = "https://slack.com/api/chat.postMessage"
    query_params = {
        "channel": "task-notifications",
        "text": f"Someone just completed the {task.title}",
    }

    headers = {"Authorization": f"Bearer {slack_token}"}
    requests.post(slack_path, params = query_params, headers = headers)

    return {
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": True
        }
    }, 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task = Task.query.get(task_id)

    if task == None:
        return make_response("Task {taske_id} not found", 404)
    task.completed_at = None

    db.session.commit()

    return {
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False
        }
    }, 200

@goals_bp.route("", methods=["POST", "GET"])
def handle_goals():
    if request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return {
                "details": f"Invalid data"
            },400
        new_goal = Goal(title=request_body["title"])
        db.session.add(new_goal)
        db.session.commit()

        return make_response({
            "goal": {
                "id": new_goal.goal_id,
                "title": new_goal.title

            }
        }, 201)
    if request.method == "GET":
        goals = Goal.query.all()
        goals_response = []
        for goal in goals:
            goals_response.append({
                "id": goal.goal_id,
                "title": goal.title
            })
        return make_response(jsonify(goals_response))

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response(f"", 404)

    if request.method == "GET":
        return make_response({
            "goal": {
                "id": goal.goal_id,
                "title": goal.title
            }
        })
    elif request.method == "PUT":
        form_data = request.get_json()
        goal.title = form_data["title"]
        db.session.commit()
        goal_response = {
            "goal": {
                "id": goal.goal_id,
                "title": goal.title
            }
        }
        return make_response(goal_response, 200)

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()

        return make_response(
            {
                "details": f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"
            }
        )
        
@goals_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handle_goals_and_tasks(goal_id):
    if request.method == "POST":
        goal = Goal.query.get(goal_id)
        if not goal:
            return make_response({
                f"Goal # {goal_id} not found."
            }, 404)
        request_body = request.get_json()
        for id in request_body["task_ids"]:
            task = Task.query.get(id)
            goal.tasks.append(task)
            db.session.add(goal)
            db.session.commit()

        return make_response({
            "id": goal.goal_id,
            "task_ids": request_body["task_ids"]
        })

    elif request.method == "GET":
        goal = Goal.query.get(goal_id)

        if not goal:
            return make_response(f"Goal {goal_id} not FOUND", 404)
        tasks = goal.tasks

        list_of_tasks = []

        for task in tasks:
            if task.completed_at == None:
                completed_at = False
            else:
                completed_at = True

            individual_task = {
                "id": task.task_id,
                "goal_id": goal.goal_id,
                "title": task.title,
                "description": task.description,
                "is_complete": completed_at
            }
            list_of_tasks.append(individual_task)
        return make_response({
            "id": goal.goal_id,
            "title": goal.title,
            "tasks": list_of_tasks
        })
