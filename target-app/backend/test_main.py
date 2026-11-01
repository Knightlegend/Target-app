import pytest
from fastapi.testclient import TestClient
from main import app
import database

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data

def test_create_and_get_tasks():
    # Create task
    payload = {
        "title": "Integration Test Task",
        "description": "Automated regression verification",
        "priority": "high",
        "status": "pending"
    }
    create_res = client.post("/api/tasks", json=payload)
    assert create_res.status_code == 201
    created_task = create_res.json()
    assert created_task["title"] == payload["title"]
    assert "id" in created_task

    # Get tasks
    get_res = client.get("/api/tasks")
    assert get_res.status_code == 200
    tasks = get_res.json()
    assert any(t["id"] == created_task["id"] for t in tasks)

    # Delete task
    del_res = client.delete(f"/api/tasks/{created_task['id']}")
    assert del_res.status_code == 200

def test_delete_nonexistent_task():
    response = client.delete("/api/tasks/999999")
    assert response.status_code == 404
