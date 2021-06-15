from app.models.task import Task
from app.models.goal import Goal
from flask import make_response
from dateutil.parser import parse, ParserError
import os
import requests

def validate_item(type, id):
    if not id.isdigit():
        return make_response(f"{id} is not a valid {type}_id. {type.title()} ID must be an integer.", 400)
    
    if type == "task":
        item = Task.query.get(id)
    elif type == "goal":
        item = Goal.query.get(id)
        
    if not item:
        return make_response(f"{type.title()} {id} not found", 404)
    return item

def validate_datetime(date_text):
    try:
        return parse(date_text)
    except ParserError:
        return  make_response(f"Invalid date format in \"completed_at\". Please resubmit with a valid date_time.", 400)
    
def post_to_slack(text):
    slack_token = os.environ.get("SLACK_POST_MESSAGE_API_TOKEN")
    slack_path = "https://slack.com/api/chat.postMessage"
    query_params ={
        "channel": "task-notifications",
        "text": text, 
    }
    headers = {"Authorization": f"Bearer {slack_token}"}
    requests.post(slack_path, params = query_params, headers = headers)   