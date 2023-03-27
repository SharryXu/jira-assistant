# -*- coding: utf-8 -*-
"""
This module is used to store excel column definition information.
"""
from typing import Any

from jira import JIRA, JIRAError


class JiraClient:
    def __init__(self, url, access_token: str) -> None:
        self.jira = JIRA(
            server=url, token_auth=access_token, timeout=20, options={"verify": False}
        )

    def health_check(self) -> bool:
        try:
            if self.jira.myself() is not None:
                return True
            else:
                return False
        except JIRAError:
            return False

    def get_stories_detail(
        self, story_ids: list[str], jira_fields: list[dict[str, str]]
    ) -> "dict[str, dict[str, str]]":
        id_query = ",".join([f"'{str(story_id)}'" for story_id in story_ids])

        try:
            search_result: dict[str, Any] = self.jira.search_issues(
                jql_str=f"id in ({id_query})",
                maxResults=len(story_ids),
                fields=[field["jira_name"] for field in jira_fields],
                json_result=True,
            )  # type: ignore

            final_result = {}
            for issue in search_result["issues"]:
                fields_result = {}
                for field in jira_fields:
                    # First element in the tuple is jira field name like "customfield_13210 or status..."
                    field_name = field["jira_name"]
                    # Remain elements represent the property path.
                    field_value: Any = issue["fields"]
                    for field_path in field["jira_path"].split("."):
                        if field_value is None:
                            field_value = ""
                            break
                        field_value = field_value.get(field_path, None)
                    fields_result[field_name] = field_value
                final_result[issue["key"].lower()] = fields_result

            return final_result
        except JIRAError as e:
            print(
                f"Calling JIRA API failed. HttpStatusCode: {e.status_code}. Response: {e.response.json()}"
            )

            return {}
