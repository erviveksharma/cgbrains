"""
Tests for the planner service.

Note: These tests require an LLM backend (Ollama/OpenAI/Anthropic).
They are integration tests and will be skipped if no LLM is available.
"""

import pytest

from app.models.step_types import QueryPlan

try:
    from app.services.planner import generate_plan

    LLM_AVAILABLE = True
except Exception:
    LLM_AVAILABLE = False

pytestmark = pytest.mark.skipif(not LLM_AVAILABLE, reason="LLM backend not available")


class TestPlannerIntegration:
    """Integration tests - require running LLM."""

    @pytest.mark.slow
    def test_simple_keyword_search(self):
        plan = generate_plan("Search Twitter for posts about climate change")
        assert isinstance(plan, QueryPlan)
        assert len(plan.steps) >= 1
        assert plan.steps[0].type == "service"
        assert plan.steps[0].service_category == "twitter_posts"

    @pytest.mark.slow
    def test_hashtag_search(self):
        plan = generate_plan("Find Instagram posts by #iranprotest")
        assert isinstance(plan, QueryPlan)
        assert len(plan.steps) >= 1
        assert plan.steps[0].service_category == "instagram_posts"
        assert plan.steps[0].initiator == "hashtag"

    @pytest.mark.slow
    def test_options_override(self):
        plan = generate_plan(
            "Search Twitter for posts about AI",
            options={"post_count": 100, "date_from": "2026-01-01"},
        )
        assert plan.metadata.post_count == 100
        assert plan.metadata.date_from == "2026-01-01"

    @pytest.mark.slow
    def test_multi_step_pipeline(self):
        plan = generate_plan(
            "Analyze sentiment of Twitter posts about @elonmusk mentioning Tesla"
        )
        assert isinstance(plan, QueryPlan)
        assert len(plan.steps) >= 2  # At least scrape + one analysis step
