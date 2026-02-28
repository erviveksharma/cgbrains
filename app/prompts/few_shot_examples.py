import json

EXAMPLES = [
    # 1. Simple URL scrape
    {
        "input": "Scrape posts from this Facebook group: https://facebook.com/groups/example",
        "plan": {
            "steps": [
                {
                    "type": "service",
                    "service_category": "facebook_posts",
                    "initiator": "url",
                    "description": "Scrap posts from Facebook group: https://facebook.com/groups/example",
                    "related_steps": [],
                    "params": {"url": "https://facebook.com/groups/example"},
                }
            ],
            "metadata": {
                "source": "facebook_posts",
                "target_url": "https://facebook.com/groups/example",
                "post_count": 50,
            },
        },
        "message": '1. [service] Scrap posts from Facebook group: https://facebook.com/groups/example',
    },
    # 2. Keyword search
    {
        "input": "Search Twitter for posts about climate change",
        "plan": {
            "steps": [
                {
                    "type": "service",
                    "service_category": "twitter_posts",
                    "initiator": "keyword",
                    "description": "Search Twitter for posts with keyword: climate change",
                    "related_steps": [],
                    "params": {"keyword": "climate change"},
                }
            ],
            "metadata": {
                "source": "twitter_posts",
                "keywords": "climate change",
                "post_count": 50,
            },
        },
        "message": '1. [service] Search Twitter for posts with keyword: climate change',
    },
    # 3. Multi-source scrape (page + keywords)
    {
        "input": "Get Instagram posts from @bbc and also search for #breakingnews",
        "plan": {
            "steps": [
                {
                    "type": "service",
                    "service_category": "instagram_posts",
                    "initiator": "username",
                    "description": "Scrap Instagram posts from user: @bbc",
                    "related_steps": [],
                    "params": {"username": "bbc"},
                },
                {
                    "type": "service",
                    "service_category": "instagram_posts",
                    "initiator": "hashtag",
                    "description": "Scrap Instagram posts associated with hashtags: #breakingnews",
                    "related_steps": [],
                    "params": {"hashtag": "breakingnews"},
                },
            ],
            "metadata": {
                "source": "instagram_posts",
                "target_name": "bbc",
                "keywords": "breakingnews",
                "post_count": 50,
            },
        },
        "message": '1. [service] Scrap Instagram posts from user: @bbc\n2. [service] Scrap Instagram posts associated with hashtags: #breakingnews',
    },
    # 4. Scrape + normalize
    {
        "input": "Scrape TikTok videos about #cooking and normalize the data",
        "plan": {
            "steps": [
                {
                    "type": "service",
                    "service_category": "tiktok_videos",
                    "initiator": "hashtag",
                    "description": "Scrap TikTok videos associated with hashtags: #cooking",
                    "related_steps": [],
                    "params": {"hashtag": "cooking"},
                },
                {
                    "type": "scripter",
                    "service_category": None,
                    "initiator": None,
                    "description": "Normalize TikTok data to standard format. Related step 1.",
                    "related_steps": [1],
                    "params": {"platform": "tiktok"},
                },
            ],
            "metadata": {
                "source": "tiktok_videos",
                "keywords": "cooking",
                "post_count": 50,
            },
        },
        "message": '1. [service] Scrap TikTok videos associated with hashtags: #cooking\n2. [scripter] Normalize TikTok data to standard format. Related step 1.',
    },
    # 5. Full CGKPIS pipeline (scrape + normalize + sentiment + keywords + target + narratives)
    {
        "input": "Analyze sentiment and narratives of Twitter posts about @elonmusk mentioning Tesla, with keywords: EV, electric, stock",
        "plan": {
            "steps": [
                {
                    "type": "service",
                    "service_category": "twitter_posts",
                    "initiator": "username",
                    "description": "Scrap tweets from user: @elonmusk",
                    "related_steps": [],
                    "params": {"username": "elonmusk"},
                },
                {
                    "type": "scripter",
                    "service_category": None,
                    "initiator": None,
                    "description": "Normalize Twitter data to standard format. Related step 1.",
                    "related_steps": [1],
                    "params": {"platform": "twitter"},
                },
                {
                    "type": "scripter",
                    "service_category": None,
                    "initiator": None,
                    "description": "Analyze sentiment of post content. Classify each post as Positive, Negative, Neutral, or Unknown. Related step 2.",
                    "related_steps": [2],
                    "params": {"operation": "sentiment"},
                },
                {
                    "type": "scripter",
                    "service_category": None,
                    "initiator": None,
                    "description": "Match posts against keywords: EV, electric, stock. Tag matching posts with attribution_tags. Related step 2.",
                    "related_steps": [2],
                    "params": {"operation": "keywords", "keywords": "EV, electric, stock"},
                },
                {
                    "type": "scripter",
                    "service_category": None,
                    "initiator": None,
                    "description": "Check if posts mention target: Tesla. Related step 2.",
                    "related_steps": [2],
                    "params": {"operation": "mentions_target", "target": "Tesla"},
                },
                {
                    "type": "scripter",
                    "service_category": None,
                    "initiator": None,
                    "description": "Classify posts into narrative categories. Related step 2.",
                    "related_steps": [2],
                    "params": {"operation": "narratives"},
                },
            ],
            "metadata": {
                "source": "twitter_posts",
                "target_name": "elonmusk",
                "keywords": "EV, electric, stock",
                "post_count": 50,
            },
        },
        "message": '1. [service] Scrap tweets from user: @elonmusk\n2. [scripter] Normalize Twitter data to standard format. Related step 1.\n3. [scripter] Analyze sentiment of post content. Classify each post as Positive, Negative, Neutral, or Unknown. Related step 2.\n4. [scripter] Match posts against keywords: EV, electric, stock. Tag matching posts with attribution_tags. Related step 2.\n5. [scripter] Check if posts mention target: Tesla. Related step 2.\n6. [scripter] Classify posts into narrative categories. Related step 2.',
    },
    # 6. Image analysis workflow
    {
        "input": "Find Instagram posts by #iranprotest and detect photo locations",
        "plan": {
            "steps": [
                {
                    "type": "service",
                    "service_category": "instagram_posts",
                    "initiator": "hashtag",
                    "description": "Scrap 50 Instagram posts associated with hashtags: #iranprotest",
                    "related_steps": [],
                    "params": {"hashtag": "iranprotest"},
                },
                {
                    "type": "service",
                    "service_category": "photo_location",
                    "initiator": "image",
                    "description": "Use photo location service to identify locations of post images. Related step 1.",
                    "related_steps": [1],
                    "params": {},
                },
            ],
            "metadata": {
                "source": "instagram_posts",
                "keywords": "iranprotest",
                "post_count": 50,
            },
        },
        "message": '1. [service] Scrap 50 Instagram posts associated with hashtags: #iranprotest\n2. [service] Use photo location service to identify locations of post images. Related step 1.',
    },
    # 7. Cross-platform profiling
    {
        "input": "Find all social media profiles for username johndoe123",
        "plan": {
            "steps": [
                {
                    "type": "service",
                    "service_category": "username_search",
                    "initiator": "username",
                    "description": "Search for username across platforms: johndoe123",
                    "related_steps": [],
                    "params": {"username": "johndoe123"},
                },
                {
                    "type": "service",
                    "service_category": "instagram_profiles",
                    "initiator": "username",
                    "description": "Get Instagram profile for username: johndoe123. Related step 1.",
                    "related_steps": [1],
                    "params": {"username": "johndoe123"},
                },
                {
                    "type": "service",
                    "service_category": "twitter_profiles",
                    "initiator": "username",
                    "description": "Get Twitter profile for username: johndoe123. Related step 1.",
                    "related_steps": [1],
                    "params": {"username": "johndoe123"},
                },
                {
                    "type": "service",
                    "service_category": "tiktok_profiles",
                    "initiator": "username",
                    "description": "Get TikTok profile for username: johndoe123. Related step 1.",
                    "related_steps": [1],
                    "params": {"username": "johndoe123"},
                },
                {
                    "type": "service",
                    "service_category": "linkedin_profiles",
                    "initiator": "username",
                    "description": "Get LinkedIn profile for username: johndoe123. Related step 1.",
                    "related_steps": [1],
                    "params": {"username": "johndoe123"},
                },
            ],
            "metadata": {
                "source": "username_search",
                "target_name": "johndoe123",
                "post_count": 50,
            },
        },
        "message": '1. [service] Search for username across platforms: johndoe123\n2. [service] Get Instagram profile for username: johndoe123. Related step 1.\n3. [service] Get Twitter profile for username: johndoe123. Related step 1.\n4. [service] Get TikTok profile for username: johndoe123. Related step 1.\n5. [service] Get LinkedIn profile for username: johndoe123. Related step 1.',
    },
    # 8. Face search from photo
    {
        "input": "Run a face search on this photo to find matching profiles",
        "plan": {
            "steps": [
                {
                    "type": "service",
                    "service_category": "facecheck_search",
                    "initiator": "image",
                    "description": "Run face recognition search to find matching profiles from uploaded photo",
                    "related_steps": [],
                    "params": {},
                },
            ],
            "metadata": {
                "source": "facecheck_search",
                "post_count": 50,
            },
        },
        "message": '1. [service] Run face recognition search to find matching profiles from uploaded photo',
    },
]


def get_few_shot_examples() -> str:
    """Format few-shot examples for the system prompt."""
    lines = ["EXAMPLES:"]
    for i, ex in enumerate(EXAMPLES, 1):
        lines.append(f"\nExample {i}:")
        lines.append(f"User: {ex['input']}")
        lines.append(f"Plan: {json.dumps(ex['plan'], indent=2)}")
    return "\n".join(lines)
