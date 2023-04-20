from __future__ import annotations

import os

from mock_server import (
    mock_jira_requests,
    mock_jira_requests_with_failed_status_code,
    mock_jira_stories,
)
from requests_mock import Mocker

from jira_assistant.jira_client import JiraClient


class TestJiraClient:
    def test_get_stories_detail(self):
        with Mocker(
            real_http=False, case_sensitive=False, adapter=mock_jira_requests()
        ):
            client = JiraClient(os.environ["JIRA_URL"], os.environ["JIRA_ACCESS_TOKEN"])

            stories = client.get_stories_detail(
                ["A-1", "A-2", "B-1"],
                [
                    {
                        "name": "domain",
                        "jira_name": "customfield_15601",
                        "jira_path": "customfield_15601.value",
                    },
                    {
                        "name": "status",
                        "jira_name": "status",
                        "jira_path": "status.name",
                    },
                ],
            )
            assert len(stories) == 3

    def test_get_stories_detail_with_large_amount_of_stories(self):
        with Mocker(
            real_http=False, case_sensitive=False, adapter=mock_jira_requests()
        ):
            client = JiraClient(os.environ["JIRA_URL"], os.environ["JIRA_ACCESS_TOKEN"])

            stories = client.get_stories_detail(
                list(mock_jira_stories.keys()),
                [
                    {
                        "name": "domain",
                        "jira_name": "customfield_15601",
                        "jira_path": "customfield_15601.value",
                    },
                    {
                        "name": "status",
                        "jira_name": "status",
                        "jira_path": "status.name",
                    },
                ],
            )
            assert len(stories) == 246

    def test_health_check(self):
        with Mocker(real_http=False, adapter=mock_jira_requests()):
            client = JiraClient(os.environ["JIRA_URL"], os.environ["JIRA_ACCESS_TOKEN"])

            assert client.health_check() is True

    def test_health_check_failed(self):
        with Mocker(
            real_http=False, adapter=mock_jira_requests_with_failed_status_code()
        ):
            client = JiraClient(os.environ["JIRA_URL"], os.environ["JIRA_ACCESS_TOKEN"])

            assert client.health_check() is False

    def test_get_stories_detail_failed(self):
        with Mocker(
            real_http=False,
            case_sensitive=False,
            adapter=mock_jira_requests_with_failed_status_code(),
        ):
            client = JiraClient(os.environ["JIRA_URL"], os.environ["JIRA_ACCESS_TOKEN"])

            stories = client.get_stories_detail(
                ["A-1", "A-2", "B-1"],
                [
                    {
                        "name": "domain",
                        "jira_name": "customfield_15601",
                        "jira_path": "customfield_15601.value",
                    },
                    {
                        "name": "status",
                        "jira_name": "status",
                        "jira_path": "status.name",
                    },
                ],
            )
            assert len(stories) == 0

    def test_get_stories_detail_with_large_amount_of_stories_failed(self):
        with Mocker(
            real_http=False,
            case_sensitive=False,
            adapter=mock_jira_requests_with_failed_status_code(),
        ):
            client = JiraClient(os.environ["JIRA_URL"], os.environ["JIRA_ACCESS_TOKEN"])

            stories = client.get_stories_detail(
                list(mock_jira_stories.keys()),
                [
                    {
                        "name": "domain",
                        "jira_name": "customfield_15601",
                        "jira_path": "customfield_15601.value",
                    },
                    {
                        "name": "status",
                        "jira_name": "status",
                        "jira_path": "status.name",
                    },
                ],
            )
            assert len(stories) == 0
