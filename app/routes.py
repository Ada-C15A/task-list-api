from app import db
from datetime import datetime
from flask import Blueprint
from flask import request
from flask import jsonify
from .models.task import Task
from .models.goal import Goal
from flask import make_response
import requests
import os
from dotenv import load_dotenv

load_dotenv()
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
        if request.method == "GET":
            tasks = Task.query.all()
            tasks_response = []
            for task in tasks:
                tasks_response.append({
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": True if task.completed_at else False
                })
            sort_by_title = request.args.get("sort")
            if sort_by_title:
                if sort_by_title == "asc":
                    tasks_response = sorted(tasks_response, key = lambda i: i['title'])
                if sort_by_title == "desc":
                    tasks_response = sorted(tasks_response, key = lambda i: i['title'],reverse=True)
            return jsonify(tasks_response), 200

        elif request.method == "POST":
            request_body = request.get_json()
            if 'title' not in request_body or 'description' not in request_body or 'completed_at' not in request_body:
                return {"details": "Invalid data"}, 400
            new_task = Task(title=request_body["title"],
                                description=request_body["description"],
                                completed_at=request_body["completed_at"])


            db.session.add(new_task)
            db.session.commit()

        return {
            "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": True if new_task.completed_at else False
            }
        }, 201

@tasks_bp.route("/<task_id>", methods=["GET", "DELETE", "PUT"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    if request.method == "GET":
        result = {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": True if task.completed_at else False
            }
        if task.goal_id:
            result["goal_id"] = task.goal_id
        return {
            "task": result
        }
    elif request.method == "DELETE":
        message = {"details": f"Task {task.task_id} \"{task.title}\" successfully deleted"}
        db.session.delete(task)
        db.session.commit()
        return make_response(message)
    elif request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]
        task.completed_at = form_data["completed_at"]

        db.session.commit()

        return make_response({
                "task": {
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": True if task.completed_at else False
                }
        })

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_task_complete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    task.completed_at = datetime.utcnow()
    db.session.commit()

    response = requests.post('https://slack.com/api/chat.postMessage', params={'channel':'task-notifications', 'text': f'Someone just completed the task {task.title}'}, headers={'Authorization': os.environ.get("SLACKBOT_API_KEY")})

    json_response = response.json()
    print(json_response)

    return make_response({
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": True
            }
    })

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_task_incomplete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    task.completed_at = None

    db.session.commit()

    return make_response({
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False
            }
    })

@goals_bp.route("", methods=["POST", "GET"])
def handle_goals():
        if request.method == "GET":
            goals = Goal.query.all()
            goals_response = []
            for goal in goals:
                goals_response.append({
                    "id": goal.goal_id,
                    "title": goal.title
                })
            sort_by_title = request.args.get("sort")
            if sort_by_title:
                if sort_by_title == "asc":
                    goals_response = sorted(goals_response, key = lambda i: i['title'])
                if sort_by_title == "desc":
                    goals_response = sorted(goals_response, key = lambda i: i['title'],reverse=True)
            return jsonify(goals_response), 200

        elif request.method == "POST":
            request_body = request.get_json()
            if 'title' not in request_body:
                return {"details": "Invalid data"}, 400
            new_goal = Goal(title=request_body["title"])

            db.session.add(new_goal)
            db.session.commit()

        return {
            "goal": {
                "id": new_goal.goal_id,
                "title": new_goal.title
            }
        }, 201

@goals_bp.route("/<goal_id>", methods=["GET", "DELETE", "PUT"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)

    if request.method == "GET":
        return {
            "goal":{
                "id": goal.goal_id,
                "title": goal.title
            }
        }
    elif request.method == "DELETE":
        message = {"details": f"Goal {goal.goal_id} \"{goal.title}\" successfully deleted"}
        db.session.delete(goal)
        db.session.commit()
        return make_response(message)
    elif request.method == "PUT":
        form_data = request.get_json()

        goal.title = form_data["title"]

        db.session.commit()

        return make_response({
                "goal": {
                    "id": goal.goal_id,
                    "title": goal.title
                }
        })

@goals_bp.route("/<goal_id>/tasks", methods=["POST", "GET"])
def handle_goal_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)

    if request.method == "GET":
        tasks = Task.query.filter(Task.goal_id == goal_id)
        results = []
        for task in tasks:
            results.append({
                "id": task.task_id,
                "goal_id": task.goal_id,
                "title": task.title,
                "description": task.description,
                "is_complete": True if task.completed_at else False
            })

        return make_response(
                {
                    "id": goal.goal_id,
                    "title": goal.title,
                    "tasks": results
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
                "id": goal.goal_id,
                "task_ids": task_ids
                }, 200)
