from app import db
from app.models.task import Task
from flask import request, Blueprint, make_response, jsonify
from datetime import datetime
import os
import json, requests
from dotenv import load_dotenv


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

load_dotenv()

def post_message_to_slack(text):
    SLACK_TOKEN = os.environ.get('SLACKBOT_TOKEN')
    slack_path = "https://slack.com/api/chat.postMessage"
    query_params ={
        'channel': 'task-notifications',
        'text': text  
    }
    headers = {'Authorization': f"Bearer {SLACK_TOKEN}"}
    requests.post(slack_path, params=query_params, headers=headers)

@tasks_bp.route("", methods=["POST", "GET"])
def handle_tasks():
    if request.method == "GET":
        title_query = request.args.get("title")
        if title_query:
            tasks = Task.query.filter(Task.title.ilike(f'%{title_query}%'))
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
                "description": task.description,
                "is_complete": bool(task.completed_at),
                "id": task.task_id,
                "title": task.title,
            })
        return jsonify(tasks_response)
    
    elif request.method == "POST":
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
        commited_task = {"task":
            {"id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete": bool(new_task.completed_at)}}
        
    return jsonify(commited_task), 201

@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == "GET":
        if task == None:
            return make_response("No matching task found", 404)
        if request.method == "GET":
            selected_task = {"task":
            {"task_id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete
            }
            }
        return selected_task
    elif request.method == "PUT":
        form_data = request.get_json()
        
        task.title = form_data["title"]
        task.description = form_data["description"]
        task.completed_at = form_data["completed_at"]
        
        db.session.commit()
        
        commited_task = {"task": 
                        {"id": task.task_id,
                        "title": task.title,
                        "description": task.description,
                        "is_complete": bool(task.completed_at)
                    }
                    }
        return jsonify(commited_task), 200
    
    elif request.method == "DELETE":        
        db.session.delete(task)
        db.session.commit()
        return jsonify(
        {f"details": 'Task 1 "Go on my daily walk 🏞" successfully deleted'}
    )

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])    
def mark_task_completed(task_id):
    task = Task.query.get_or_404(task_id)            
    task.completed_at = datetime.now()
    
    db.session.commit() 
    slack_message = f"Someone just completed the task {task.title}"
    post_message_to_slack(slack_message)

    completed_task = {"task": 
            {"id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": True
        }
        }
    return jsonify(completed_task), 200 

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_incomplete(task_id):
    task = Task.query.get_or_404(task_id)            
    task.completed_at = None
    
    db.session.commit() 
    incomplete_task = {"task": 
            {"id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
        }
        }
    return jsonify(incomplete_task), 200 