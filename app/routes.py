import re
from app.models.task import Task
from app.models.goal import Goal
from app import db 
from flask import request, Blueprint, make_response, jsonify#
from datetime import datetime
import os
import json, requests
from dotenv import load_dotenv

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks") 
goals_bp = Blueprint("goals", __name__, url_prefix="/goals") 

load_dotenv()

def post_message_to_slack(text):
    SLACK_TOKEN = os.environ.get('SLACKBOT_TOKEN')
    slack_path = "https://slack.com/api/chat/postMessage"
    query_params = {
        'channel': 'task-notifications',
        'text': text 
    }
    headers = {'Authorization': f"Bearer {SLACK_TOKEN}"}
    request.post(slack_path, params=query_params, headers=headers)

@goals_bp.route("", methods=["GET", "POST"])
def handle_goals():
    if request.method == "POST": 
        request_body = request.get_json()
        title = request_body.get("title")

        if "title" not in request_body:
            return jsonify({"details": "Invalid data"}), 400

        new_goal = Goal(title=request_body["title"])

        db.session.add(new_goal)
        db.session.commit()

        committed_goal = {
            "goal": {
                "id": new_goal.goal_id,
                "title": new_goal.title
            }
        }

        return jsonify(committed_goal), 201

    elif request.method == "GET":
        goals = Goal.query.all()
        goals_response = []
        
        for goal in goals:
            goals_response.append({
                "title": goal.title,
                "id": goal.goal_id
            })

        return jsonify(goals_response), 200

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    
    if request.method =="GET":
        if goal == None:
            return make_response("No matching goal found"), 404

        tasks = []

        for item in goal.tasks:
            tasks.append(item)
        
        selected_goal = {"goal": 
            {"id": goal.goal_id,
            "title": goal.title,
            "tasks": tasks
            }}
        return selected_goal

    elif request.method == "PUT":
        form_data = request.get_json()
        goal.title = form_data["title"]

        db.session.commit()

        committed_goal = {"goal": 
            {"id": goal.goal_id,
            "title": goal.title,
            }}
        return jsonify(committed_goal), 200
    
    elif request.method == "DELETE":
        db.session.delete(goal)
        db.session.commit()
        goal_response_body = {
            "details":
                f'Goal {goal.goal_id} successfully deleted'
            }
        return jsonify(goal_response_body)

@goals_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handle_goal_tasks(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    if request.method == "GET":
        tasks = goal.tasks
        list_of_tasks = []
        
        for task in tasks:
            if task.completed_at == None:
                completed_at = False
            else:
                completed_at = True

            individual_task = {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": completed_at,
                "goal_id": goal.goal_id
            }
            list_of_tasks.append(individual_task)

        return make_response({
            "id": goal.goal_id,
            "title": goal.title,
            "tasks": list_of_tasks
        })

    if request.method == "POST":
        goal = Goal.query.get(goal_id)
        request_body = request.get_json()

        for ids_per_task in request_body["task_ids"]:
            task = Task.query.get(ids_per_task)
            goal.tasks.append(task)
            db.session.add(goal)
            db.session.commit()

        return make_response({
            "id": goal.goal_id,
            "task_ids": request_body["task_ids"]
        })

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "POST": 
        request_body = request.get_json()
        title = request_body.get("title")
        description = request_body.get("description")

        if not title or not description or "completed_at" not in request_body:
            return make_response(jsonify({"details": "Invalid data"}), 400)

        new_task = Task(
                    title=request_body["title"],
                    description=request_body["description"],
                    completed_at=request_body["completed_at"])

        if new_task.completed_at == None:
            completed_at = False
        else:
            completed_at = True

        db.session.add(new_task)
        db.session.commit()

        return make_response({
            "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": completed_at
            }}, 201)

    elif request.method == "GET":
        url_title = request.args.get("title")
        if url_title:
            tasks = Task.query.filter_by(title=url_title)
        else: 
            tasks = Task.query.order_by(Task.title).all()

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
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": bool(task.completed_at),
                "goal": task.goal_id
            })
        return jsonify(tasks_response)

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE", "PATCH"])    
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("No matching task found", 404)

    if request.method == "GET":

        if task.completed_at == None:
            completed_at = False
        else:
            completed_at = True

        selected_task = {
            "task": {
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": completed_at
            }
        }

        if task.goal_id == None:
            return make_response(selected_task)
        else:
            return make_response({
                "task": {
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": completed_at,
                    "goal_id": task.goal_id
                }
            })

    elif request.method == "PUT": 
        request_body = request.get_json()

        task.title = request_body["title"]
        task.description = request_body["description"]
        task.completed_at = request_body["completed_at"]

        updated_task = {"task": 
            {"id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
        }}
        db.session.add(task)
        db.session.commit()

        return make_response(jsonify(updated_task)), 200

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        task_response_body = {
            "details":
                f'Task {task.task_id} \"{task.title}\" successfully deleted'
            }
        return jsonify(task_response_body), 200

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_complete(task_id):
    task = Task.query.get_or_404(task_id)

    task.completed_at = datetime.now()

    db.session.commit()

    slack_message = f"A user just completed task: {task.title}"
    post_message_to_slack(slack_message)

    completed_task = {"task": 

            {"id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
        }}
    return jsonify(completed_task), 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_incomplete(task_id):
    task = Task.query.get_or_404(task_id)

    task.completed_at = None
    db.session.commit()
    incompleted_task = {"task": 

            {"id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
        }}
    return jsonify(incompleted_task), 200


# https://github.com/OhCloud/task-list-api
# https://github.com/Ada-C15A/task-list-api/pull/3