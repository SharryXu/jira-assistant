import os
import pathlib

import pytest

from jira_assistant.jira_client import *

HERE = pathlib.Path(__file__).resolve().parent


@pytest.mark.skipif(
    os.environ.get("JIRA_ACCESS_TOKEN") is None, reason="Security Consideration."
)
class TestJiraClient:
    def setup_method(self, method):
        self.client = JiraClient(
            os.environ["JIRA_URL"], os.environ["JIRA_ACCESS_TOKEN"]
        )

    def test_get_stories_detail(self):
        stories = self.client.get_stories_detail(
            ["TAX-36953", "TAX-35921", "WEB-68966", "GSS-35877"],
            [
                {
                    "name": "domain",
                    "jira_name": "customfield_15601",
                    "jira_path": "customfield_15601.value",
                },
                {"name": "status", "jira_name": "status", "jira_path": "status.name"},
            ],
        )
        assert len(stories) == 4

    def test_health_check(self):
        assert self.client.health_check() is True
