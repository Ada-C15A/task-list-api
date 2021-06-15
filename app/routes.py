from flask import Blueprint, request, jsonify, make_response
from app import db
from app.models.task import Task
from datetime import datetime

task_list_api_bp = Blueprint("task_list_api", __name__, url_prefix="/tasks")


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
                "id": 1,
                "title": "Updated Task Title",
                "description": "Updated Test Description",
                "is_complete": True if task.completed_at else False
            }
        }, 200


@task_list_api_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return make_response(f"{task_id} doesnt exist", 404)
    task.completed_at = datetime.utcnow()

    db.session.commit()

    if request.method == "PATCH":
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
