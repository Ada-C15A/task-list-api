from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import json, request, Blueprint, make_response, jsonify
from datetime import datetime
import os
import requests

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        title_from_url = request.args.get("title")
        if title_from_url:
            tasks = Task.query.filter_by(title=title_from_url)
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
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)
            })
        return jsonify(tasks_response)

    elif request.method == "POST":
        request_body = request.get_json()
        title = request_body.get("title")
        description = request_body.get("description")

        if not title or not description or "completed_at" not in request_body:
            return jsonify({"details": "Invalid data"}), 400

        new_task = Task(title=title,
                        description=description,
                        completed_at=request_body["completed_at"])
        db.session.add(new_task)
        db.session.commit()
        commited_task = {"task":
            {"id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": bool(new_task.completed_at)
        }}
        return jsonify(commited_task), 201

@tasks_bp.route("/<tasks_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(tasks_id):
    task = Task.query.get_or_404(tasks_id)
    if request.method == "GET":
        if task.goal_id != None:
            selected_task = {"task":
            {"id": task.id,
            "goal_id": task.goal_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
            }}
        else:
            selected_task = {"task":
            {"id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
            }}
        return jsonify(selected_task),200

    elif request.method == "PUT":
        request_body = request.get_json()
        task.title = request_body["title"]
        task.description = request_body["description"]
        task.completed_at = request_body["completed_at"]
        updated_task = {'task':{
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)
            }}
        db.session.commit()
        return jsonify(updated_task),200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        task_response_body = {"details": f'Task {task.id} "{task.title}" successfully deleted'}
        return jsonify(task_response_body),200

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_task_complete(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed_at = datetime.now()
    
    db.session.commit()

    patched_task = {"task": {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_complete": True
        }}
    return jsonify(patched_task),200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_task_incomplete(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed_at = None

    db.session.commit()

    patched_task = {"task": {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_complete": False
        }}
    return jsonify(patched_task),200

# Slack Portion
def post_to_slack(text):
    slack_token = os.environ.get("SLACK_TOKEN_POST")
    slack_path = "https://slack.com/api/chat.postMessage"
    query_params = {
        "channel": "task-notification",
        "text": text,
    }
    headers = {
        "Authorization": f"Bearer {slack_token}"
    }
    requests.post(slack_path, params=query_params, headers=headers)

# Goals Route Portion
goal_bp = Blueprint("goal_bp", __name__, url_prefix="/goals")

@goal_bp.route("", methods=["GET", "POST"])
def handle_goals():
    if request.method == "GET":
        goals = Goal.query.all()
        goals_response = []
        for goal in goals:
            goals_response.append({
                "id": goal.goal_id,
                "title": goal.title,
            })
        return jsonify(goals_response), 200
    elif request.method == "POST":
        request_body = request.get_json()
        title = request_body.get("title")
        if not title:
            return jsonify({"details": "Invalid data"}), 400
        new_goal = Goal(title=request_body["title"])
            
        db.session.add(new_goal)
        db.session.commit()
        goal_response_body = {"goal": {"id": new_goal.goal_id, "title": new_goal.title}}
        
        return jsonify(goal_response_body), 201

@goal_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if request.method == "GET":
        selected_goal = {"goal":
            {"title": goal.title,
            "id": goal.goal_id
            }}
        return jsonify(selected_goal), 200
    elif request.method == "PUT":
        request_body = request.get_json()
        goal.title = request_body["title"]
        updated_goal = {'goal':{
                "id": goal.goal_id,
                "title": goal.title
            }}
        db.session.commit()
        return jsonify(updated_goal),200

    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        goal_response_body = {"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}
        return jsonify(goal_response_body),200

@goal_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handle_goals_and_tasks(goal_id):
    if request.method == "POST":
        goal = Goal.query.get_or_404(goal_id)
        request_body = request.get_json()
        for id in request_body["task_ids"]:
            task = Task.query.get(id)
            goal.tasks.append(task)
            db.session.add(goal)
            db.session.commit()

        goal_task_response_body = {"id": goal.goal_id, "task_ids": request_body["task_ids"]}
        return jsonify(goal_task_response_body), 200

    elif request.method == "GET":
        goal = Goal.query.get_or_404(goal_id)
        tasks = goal.tasks
        list_of_tasks = []

        for task in tasks:
            individual_task = {
                "id": task.id,
                "goal_id": goal.goal_id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at)
            }
            list_of_tasks.append(individual_task)
        goal_task_get_response_body = {"id": goal.goal_id, "title": goal.title,"tasks": list_of_tasks}
        return jsonify(goal_task_get_response_body), 200
