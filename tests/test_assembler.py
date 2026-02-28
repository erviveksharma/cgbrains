from app.models.step_types import QueryMetadata, QueryPlan, StepPlan
from app.services.assembler import build_message, build_response


def _make_plan(steps: list[StepPlan], **meta_kwargs) -> QueryPlan:
    return QueryPlan(steps=steps, metadata=QueryMetadata(**meta_kwargs))


class TestBuildMessage:
    def test_single_service_step(self):
        plan = _make_plan(
            steps=[
                StepPlan(
                    type="service",
                    service_category="twitter_posts",
                    initiator="keyword",
                    description="Search Twitter for posts with keyword: climate change",
                ),
            ],
            source="twitter_posts",
        )
        msg = build_message(plan)
        assert msg == "1. [service] Search Twitter for posts with keyword: climate change"

    def test_multi_step_with_related(self):
        plan = _make_plan(
            steps=[
                StepPlan(
                    type="service",
                    service_category="instagram_posts",
                    initiator="hashtag",
                    description="Scrap Instagram posts associated with hashtags: #protest",
                ),
                StepPlan(
                    type="service",
                    service_category="photo_location",
                    initiator="image",
                    description="Use photo location service to identify locations. Related step 1.",
                    related_steps=[1],
                ),
            ],
            source="instagram_posts",
        )
        msg = build_message(plan)
        lines = msg.split("\n")
        assert len(lines) == 2
        assert lines[0].startswith("1. [service]")
        assert lines[1].startswith("2. [service]")
        assert "Related step 1" in lines[1]

    def test_scripter_normalize_template(self):
        plan = _make_plan(
            steps=[
                StepPlan(
                    type="service",
                    service_category="twitter_posts",
                    initiator="keyword",
                    description="Search Twitter for posts",
                ),
                StepPlan(
                    type="scripter",
                    description="Normalize Twitter data. Related step 1.",
                    related_steps=[1],
                    params={"operation": "normalize", "platform": "twitter"},
                ),
            ],
            source="twitter_posts",
        )
        msg = build_message(plan)
        assert "[scripter]" in msg
        assert "tweet_id" in msg  # twitter normalize template content

    def test_scripter_sentiment_template(self):
        plan = _make_plan(
            steps=[
                StepPlan(
                    type="scripter",
                    description="Analyze sentiment",
                    params={"operation": "sentiment"},
                ),
            ],
        )
        msg = build_message(plan)
        assert "Positive" in msg
        assert "Negative" in msg

    def test_scripter_keywords_template(self):
        plan = _make_plan(
            steps=[
                StepPlan(
                    type="scripter",
                    description="Match keywords",
                    params={"operation": "keywords", "keywords": "EV, electric, stock"},
                ),
            ],
        )
        msg = build_message(plan)
        assert "EV, electric, stock" in msg
        assert "attribution_tags" in msg

    def test_ai_step(self):
        plan = _make_plan(
            steps=[
                StepPlan(
                    type="ai",
                    description="Classify posts by topic: politics, economy, social",
                ),
            ],
        )
        msg = build_message(plan)
        assert msg == "1. [ai] Classify posts by topic: politics, economy, social"

    def test_ai_image_step(self):
        plan = _make_plan(
            steps=[
                StepPlan(
                    type="ai-image",
                    description="Detect objects in post images",
                ),
            ],
        )
        msg = build_message(plan)
        assert msg == "1. [ai-image] Detect objects in post images"


class TestBuildResponse:
    def test_response_structure(self):
        plan = _make_plan(
            steps=[
                StepPlan(
                    type="service",
                    service_category="twitter_posts",
                    initiator="keyword",
                    description="Search Twitter",
                ),
            ],
            source="twitter_posts",
            target_name="test",
        )
        message = "1. [service] Search Twitter"
        resp = build_response(plan, message)

        assert resp.success is True
        assert resp.step_count == 1
        assert resp.steps[0].number == 1
        assert resp.steps[0].type == "service"
        assert resp.params.source == "twitter_posts"
        assert resp.params.target_name == "test"
