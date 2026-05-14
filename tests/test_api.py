from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_endpoint_schema_validation():
    # Should fail if missing messages
    response = client.post("/chat", json={})
    assert response.status_code == 422

def test_chat_endpoint_empty_messages():
    response = client.post("/chat", json={"messages": []})
    assert response.status_code == 400
    assert "No user message provided" in response.json()["detail"]

def test_chat_endpoint_guardrail():
    # Test refusal policy for off-topic queries
    response = client.post("/chat", json={
        "messages": [
            {"role": "user", "content": "What is the average salary for a Java Developer?"}
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "I can only assist with" in data["reply"]
    assert len(data["recommendations"]) == 0
    assert data["end_of_conversation"] is False
