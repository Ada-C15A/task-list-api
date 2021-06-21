from flask import Blueprint, request, jsonify, make_response
from app import db
from app.models.task import Task
from app.models.goal import Goal
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

load_dotenv()

task_list_api_bp = Blueprint("task_list_api", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")


@task_list_api_bp.route("", methods=["GET", "POST"])
def tasks():
    if request.method == "GET":
        tasks_sort = request.args.get("sort")
        tasks = Task.query.all()

        if tasks_sort:
            if tasks_sort == "asc":
                tasks = Task.query.order_by(Task.title).all()
            elif tasks_sort == "desc":
                tasks = Task.query.order_by(Task.title.desc()).all()
            else:
                tasks = Task.query.all()

        tasks_response = []
        # is_complete = task.completed_at

        for task in tasks:
            is_complete = task.completed_at
            if task.completed_at != None:
                is_complete = True
            elif tasks_sort and task.completed_at is None:
                is_complete = False

            tasks_response.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": is_complete
            })

        return jsonify(tasks_response)

    elif request.method == "POST":

        request_body = request.get_json(force=True)

        if 'title' not in request_body or 'description' not in request_body or 'completed_at' not in request_body:
            return {"details": "Invalid data"}, 400
        new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body["completed_at"])
        db.session.add(new_task)
        db.session.commit()

        return {
            "task": {
                "id": new_task.id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": True if new_task.completed_at else False
            }
        }, 201


@task_list_api_bp.route("/<task_id>", methods=["GET", "DELETE", "PUT"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response(f"{task_id} doesnt exist", 404)

    # is_complete = task.completed_at
    # if task.completed_at != None:
    #     is_complete == True
    # print(is_complete)

    if request.method == "GET":
        select_task = {
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.completed_at
            }
        }
        return jsonify(select_task), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return make_response({"details": f"Task {task.id} \"{task.title}\" successfully deleted"})

    elif request.method == "PUT":
        form_data = request.get_json()
        task.title = form_data["title"]
        task.description = form_data["description"]
        completed_at = form_data["completed_at"]

        db.session.commit()

        return {
            "task": {
                "id": task.id,
                "title": "Updated Task Title",
                "description": "Updated Test Description",
                "is_complete": True if task.completed_at else False
            }
        }, 200


def post_slack(message_slack):

    TOKEN_SLACK = os.environ.get(
        "SLACK_BOT_TOKEN")
    slack_path = "https://slack.com/api/chat.postMessage"
    query_params = {
        'channel': 'task-notifications',
        'text': message_slack
    }
    headers = {'Authorization': f"Bearer {TOKEN_SLACK}"}
    requests.post(slack_path, params=query_params, headers=headers)


@task_list_api_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response(f"{task_id} doesnt exist", 404)
    task.completed_at = datetime.utcnow()

    db.session.commit()

    if request.method == "PATCH":
        message_slack = f"Someone just completed the task: {task.title}"
        post_slack(message_slack)
        return {
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": True if task.completed_at else False
            }
        }, 200


@task_list_api_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response(f"{task_id} doesnt exist", 404)

    task.completed_at = None
    db.session.commit()

    if request.method == "PATCH":
        return {
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete":  True if task.completed_at else False
            }
        }, 200


@goals_bp.route("", methods=["GET", "POST"])
def handle_goals():
    if request.method == "GET":
        goals = Goal.query.all()

        goals_response = []

        for goal in goals:
            print(goal.title)
            print(goal.id)
            goals_response.append({
                "id": goal.id,
                "title": goal.title
            })

        return jsonify(goals_response)

    elif request.method == "POST":

        request_body = request.get_json(force=True)
        if "title" not in request_body:
            return {"details": "Invalid data"}, 400
        new_goal = Goal(title=request_body["title"])

        db.session.add(new_goal)
        db.session.commit()

        return make_response(
            {
                "goal": {
                    "id": new_goal.id,
                    "title": new_goal.title
                }
            }, 201
        )


@goals_bp.route("/<goal_id>", methods=["GET", "DELETE", "PUT"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response(f"{goal_id} doesnt exist", 404)

    if request.method == "GET":
        select_goal = {
            "goal": {
                "id": goal.id,
                "title": goal.title
            }
        }
        return jsonify(select_goal), 200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        return make_response({"details": f"Goal {goal.id} \"{goal.title}\" successfully deleted"})

    elif request.method == "PUT":
        form_data = request.get_json()
        goal.title = form_data["title"]

        db.session.commit()

        return {
            "goal": {
                "id": goal.id,
                "title": "Updated Goal Title",
            }
        }, 200


@goals_bp.route("/<goal_id>/tasks", methods=["POST", "GET"])
def handle_goal_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response(f"{goal_id} doesnt exist", 404)

    if request.method == "GET":
        tasks = Task.query.filter(Task.goal_id == goal_id)
        all_goal_tasks = []

        for task in tasks:
            all_goal_tasks.append({
                "id": task.id,
                "goal_id": goal.id,
                "title": task.title,
                "description": task.description,
                "is_complete": True if task.completed_at else False
            })

        return make_response(
            {
                "id": goal.id,
                "title": goal.title,
                "tasks": all_goal_tasks
            }, 200)

    elif request.method == "POST":
        form_data = request.get_json()
        task_ids = form_data['task_ids']

        for id in task_ids:
            task = Task.query.get(id)
            task.goal_id = goal_id

        db.session.commit()

        return make_response(
            {
                "id": goal.id,
                "task_ids": task_ids
            }, 200)
