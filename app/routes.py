from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import request, Blueprint, make_response, jsonify
from sqlalchemy import desc
from datetime import date
import requests, os

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

''''''''''''''''''''''''''''''''''''
# # # # # # TASK ROUTES # # # # # #
''''''''''''''''''''''''''''''''''''

@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    if request.method == "POST":
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
        db_task = {
            "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": bool(new_task.completed_at)
            }
        }
        return db_task, 201
    
    elif request.method == "GET":
        if request.args.get("sort") == "asc":
            tasks = Task.query.order_by(Task.title)
        elif request.args.get("sort") == "desc":
            tasks = Task.query.order_by(desc(Task.title))
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


@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    if request.method == "GET":
        selected_task = {
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)
            }
        }
        return selected_task

    elif request.method == "PUT":
        request_body = request.get_json()

        task.title = request_body["title"]
        task.description = request_body["description"]
        task.completed_at = request_body["completed_at"]

        updated_task = {
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)
            }
        }

        db.session.commit()
        return make_response(updated_task, 200)

    elif request.method == "DELETE":
        response = {
            "details":
            f'Task {task.task_id} "{task.title}" successfully deleted'
        }
        db.session.delete(task)
        db.session.commit()
        return make_response(response, 200)

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_complete_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    task.completed_at = date.today()
    db.session.commit()
    response = {
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": True
        }
    }

    slack_path = "https://slack.com/api/chat.postMessage"
    slack_token = os.environ.get("SLACK_API_TOKEN")
    slack_headers = {
        "Authorization": f"Bearer {slack_token}"
    }
    slack_query_params = {
        "channel": "task-list-bot",
        "text": f"Someone just completed the task {task.title}."
    }
    requests.post(slack_path, params=slack_query_params, headers=slack_headers)

    return make_response(response, 200)

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_incomplete_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    task.completed_at = None
    db.session.commit()
    response = {
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False
        }
    }
    return make_response(response, 200)

''''''''''''''''''''''''''''''''''''
# # # # # # GOAL ROUTES # # # # # #
''''''''''''''''''''''''''''''''''''

@goals_bp.route("", methods=["POST", "GET"])
def handle_goals():
    if request.method == "POST":
        request_body = request.get_json()
        title = request_body.get("title")

        if not title:
            response_body = {"details": "Invalid data"}
            return make_response(response_body, 400)

        new_goal = Goal(title=title)
        db.session.add(new_goal)
        db.session.commit()
        db_goal = {
            "goal": {
                "id": new_goal.goal_id,
                "title": new_goal.title
            }
        }
        return db_goal, 201
    elif request.method == "GET":
        goals = Goal.query.all()

        goals_response = []
        for goal in goals:
            goals_response.append({
                "id": goal.goal_id,
                "title": goal.title
            })
        goals_json_response = jsonify(goals_response)
        return make_response(goals_json_response, 200)

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)

    if request.method == "GET":
        selected_goal = {
            "goal": {
                "id": goal.goal_id,
                "title": goal.title}
        }
        return make_response(selected_goal, 200)

    elif request.method == "PUT":
        request_body = request.get_json()

        goal.title = request_body["title"]

        updated_goal = {
            "goal": {
                "id": goal.goal_id,
                "title": goal.title
            }
        }

        db.session.commit()
        return make_response(updated_goal, 200)

    elif request.method == "DELETE":
        response = {
            "details":
            f'Goal {goal.goal_id} "{goal.title}" successfully deleted'
        }
        db.session.delete(goal)
        db.session.commit()
        return make_response(response, 200)