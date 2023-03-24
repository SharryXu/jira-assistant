# -*- coding: utf-8 -*-
"""
This module is used to store excel column definition information.
"""
import json
from typing import Any

from requests import Response, get, post
from requests.exceptions import RequestException
from requests.status_codes import codes


class JiraClient:
    def __init__(self, url, access_token: str) -> None:
        self.base_url: str = url
        self.timeout: int = 20
        self.access_token: str = access_token
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

    def health_check(self) -> bool:
        url = f"{self.base_url}/rest/api/2/dashboard?maxResults=1"

        try:
            response: Response = get(
                url,
                headers=self.headers,
                verify=False,
                timeout=self.timeout,
            )

            if response.status_code == codes["OK"]:
                return True
        except RequestException as e:
            print(e)
        return False

    def get_stories_detail(
        self, story_ids: list[str], jira_fields: list[dict[str, str]]
    ) -> "dict[str, dict[str, str]]":
        url = f"{self.base_url}/rest/api/2/search"
        id_query = ",".join([f"'{str(story_id)}'" for story_id in story_ids])
        request_body = json.dumps(
            {
                "expand": [],
                "jql": f"id in ({id_query})",
                "maxResults": len(story_ids),
                "fields": [field["jira_name"] for field in jira_fields],
                "startAt": 0,
            }
        )

        try:
            response: Response = post(
                url,
                data=request_body,
                headers=self.headers,
                verify=False,
                timeout=self.timeout,
            )

            if response.status_code == codes["OK"]:
                search_result = response.json()

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
            else:
                return {}
        except RequestException as e:
            print(e)

            return {}
