from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from app.main import app, engine
from app.models.step_types import QueryMetadata, QueryPlan, StepPlan

# Ensure tables exist for tests
SQLModel.metadata.create_all(engine)

client = TestClient(app)


def _mock_plan():
    return QueryPlan(
        steps=[
            StepPlan(
                type="service",
                service_category="twitter_posts",
                initiator="keyword",
                description="Search Twitter for posts with keyword: climate change",
            ),
        ],
        metadata=QueryMetadata(
            source="twitter_posts",
            keywords="climate change",
            post_count=50,
        ),
    )


class TestHealthEndpoint:
    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestServicesEndpoint:
    def test_services_returns_list(self):
        response = client.get("/services")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data
        assert len(data["services"]) > 0

    def test_services_have_categories(self):
        response = client.get("/services")
        data = response.json()
        first = data["services"][0]
        assert "category" in first
        assert "initiators" in first
        assert "services" in first


class TestGenerateEndpoint:
    @patch("app.main.generate_plan")
    def test_generate_success(self, mock_plan):
        mock_plan.return_value = _mock_plan()

        response = client.post("/generate", json={
            "prompt": "Search Twitter for posts about climate change",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["step_count"] == 1
        assert len(data["steps"]) == 1
        assert data["steps"][0]["type"] == "service"
        assert "[service]" in data["message"]

    @patch("app.main.generate_plan")
    def test_generate_with_options(self, mock_plan):
        mock_plan.return_value = _mock_plan()

        response = client.post("/generate", json={
            "prompt": "Search Twitter for posts about AI",
            "options": {"post_count": 100},
        })
        assert response.status_code == 200

    @patch("app.main.generate_plan", side_effect=Exception("LLM error"))
    def test_generate_error(self, mock_plan):
        response = client.post("/generate", json={
            "prompt": "test",
        })
        assert response.status_code == 500


class TestFeedbackEndpoint:
    def test_feedback_success(self):
        response = client.post("/feedback", json={
            "user_id": 1,
            "input_prompt": "Search Twitter",
            "generated_message": "1. [service] Search Twitter",
            "final_message": "1. [service] Search Twitter for posts",
            "rating": 4,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "id" in data

    def test_feedback_invalid_rating(self):
        response = client.post("/feedback", json={
            "user_id": 1,
            "input_prompt": "test",
            "generated_message": "test",
            "final_message": "test",
            "rating": 6,
        })
        assert response.status_code == 422
