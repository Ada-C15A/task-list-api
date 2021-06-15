from app.models.task import Task
import datetime

def test_create_task_with_valid_datetime_string(client):
    # Act
    response = client.post("/tasks", json={
        "title": "A Brand New Task",
        "description": "Test Description",
        "completed_at": "June 24, 2021 11:00:00"
    })
    response_body = response.get_json()

    # Assert
    assert response.status_code == 201
    assert response_body == {
        "task": {
        "description": "Test Description",
        "id": 1,
        "is_complete": True,
        "title": "A Brand New Task"
    }
    }
    task = Task.query.get(1)
    assert task.title == "A Brand New Task"
    assert task.description == "Test Description"
    assert task.completed_at == datetime.datetime(2021, 6, 24, 11, 0)

    
def test_create_task_with_invalid_datetime_string(client):
    # Act
    response = client.post("/tasks", json={
        "title": "A Brand New Task",
        "description": "Test Description",
        "completed_at": "Just finished"
    })
    response_text = response.get_data(as_text=True)

    # Assert
    assert response.status_code == 400
    assert response_text == f"Invalid date format in \"completed_at\". Please resubmit with a valid date_time."
    assert Task.query.all() == []

def test_update_task_with_valid_datetime_string(client, one_task):
    # Act
    response = client.put("/tasks/1", json={
        "title": "Updated Task Title",
        "description": "Updated Test Description",
        "completed_at": "June 28, 2020"
    })
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert "task" in response_body
    assert response_body == {
        "task": {
            "id": 1,
            "title": "Updated Task Title",
            "description": "Updated Test Description",
            "is_complete": True
        }
    }
    task = Task.query.get(1)
    assert task.title == "Updated Task Title"
    assert task.description == "Updated Test Description"
    assert task.completed_at == datetime.datetime(2020, 6, 28, 0, 0)


def test_update_task_with_invalid_datetime_string(client, one_task):
    # Act
    response = client.put("/tasks/1", json={
        "title": "A Brand New Task",
        "description": "Test Description",
        "completed_at": "Just finished"
    })
    response_text = response.get_data(as_text=True)

    # Assert
    assert response.status_code == 400
    assert response_text == f"Invalid date format in \"completed_at\". Please resubmit with a valid date_time."
    assert Task.query.first().title == "Go on my daily walk 🏞"
    assert Task.query.first().description == "Notice something new every day"    
    assert Task.query.first().completed_at == None

def test_get_tasks_invalid_sort_param(client, three_tasks):
    # Act
    response = client.get("/tasks?sort=ASC")
    response_text = response.get_data(as_text=True)

    # Assert
    assert response.status_code == 400
    assert response_text == "ASC is not a valid sort parameter. Please use sort=asc or sort=desc."
    
def test_task_to_json_no_goal(one_task):
    # Arrange
    task = Task.query.first()
    
    # Act
    task_json = task.to_json()
    
    # Assert
    assert task_json["id"] == task.id
    assert task_json["title"] == task.title
    assert task_json["description"] == task.description
    assert task_json["is_complete"] == task.is_complete()
    assert task_json.get("goal_id") == None

def test_task_to_json_with_goal(one_task_belongs_to_one_goal):
    # Arrange
    task = Task.query.first()
    
    # Act
    task_json = task.to_json()
    
    # Assert
    assert task_json["id"] == task.id
    assert task_json["title"] == task.title
    assert task_json["description"] == task.description
    assert task_json["is_complete"] == task.is_complete()
    assert task_json.get("goal_id") == task.goal_id