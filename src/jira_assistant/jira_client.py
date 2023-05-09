# -*- coding: utf-8 -*-
"""
This module is used to store excel column definition information.
"""
import warnings
from typing import Any, Dict, List

from jira import JIRA, JIRAError
from urllib3 import disable_warnings

from .story import Story
from .utils import JiraFieldTypeDefinition, get_jira_field_type

# Currently, the openpyxl package will report an obsolete warning.
warnings.simplefilter(action="ignore", category=UserWarning)
# Disable the HTTPS certificate verification warning.
disable_warnings()


class JiraClient:
    def __init__(self, url: str, access_token: str) -> None:
        self.jira = JIRA(
            server=url,
            token_auth=access_token,
            timeout=20,
            options={"verify": False},
        )
        self._field_cache: Dict[str, Dict[str, str]] = {}

    def health_check(self) -> bool:
        try:
            if self.jira.myself() is not None:
                return True
            return False
        except JIRAError:
            return False

    def create_storys(self, storys: List[Story]) -> "List[Story]":
        # self.jira.create_issues(, prefetch=true)
        return storys

    def get_all_fields(self) -> "Dict[str, Dict[str, str]]":
        if not self._field_cache:
            for field in self.jira.fields():
                temp = {
                    "id": field["id"],
                    "isArray": False,
                }

                if "schema" in field and "type" in field["schema"]:
                    field_type: JiraFieldTypeDefinition | None = get_jira_field_type(
                        field["schema"]["type"]
                    )

                    if field_type is not None:
                        if field_type.get("isBasic", None) is True:
                            temp["path"] = field["name"]
                        elif field_type.get("isArray", None) is True:
                            field_type = field["schema"]["items"]
                            if field_type is not None:
                                temp["isArray"] = True
                        else:
                            temp["path"] = ""
                self._field_cache[field["name"]] = temp
        return self._field_cache

    def get_stories_detail(
        self, story_ids: List[str], jira_fields: List[Dict[str, str]]
    ) -> "Dict[str, Dict[str, str]]":
        final_result = {}
        batch_size = 200

        try:
            if len(story_ids) > batch_size:
                start_index = 0
                end_index = batch_size
                while end_index <= len(story_ids) and start_index < len(story_ids):
                    # print(f"Start: {start_index}, End: {end_index}")
                    final_result.update(
                        self._internal_get_stories_detail(
                            story_ids[start_index:end_index], jira_fields
                        )
                    )
                    start_index = end_index
                    if start_index + batch_size < len(story_ids):
                        end_index = start_index + batch_size
                    else:
                        end_index = start_index + (len(story_ids) - end_index)
                return final_result

            return self._internal_get_stories_detail(story_ids, jira_fields)
        except JIRAError as e:
            print(
                f"Calling JIRA API failed. HttpStatusCode: {e.status_code}. Response: {e.response.json()}"
            )

            return {}

    def _internal_get_stories_detail(
        self, story_ids: List[str], jira_fields: List[Dict[str, str]]
    ) -> "Dict[str, Dict[str, str]]":
        id_query = ",".join([f"'{str(story_id)}'" for story_id in story_ids])

        try:
            search_result: Dict[str, Any] = self.jira.search_issues(
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
