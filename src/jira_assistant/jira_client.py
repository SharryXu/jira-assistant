# -*- coding: utf-8 -*-
"""
This module is used to store excel column definition information.
"""
import warnings
from sys import version_info
from typing import Any, Dict, List, Optional, TypedDict, Union

from jira import JIRA, JIRAError
from urllib3 import disable_warnings

from .story import Story
from .utils import JiraFieldTypeDefinition, get_jira_field_type

if version_info < (3, 11):
    from typing_extensions import NotRequired
else:
    from typing import NotRequired

# Currently, the openpyxl package will report an obsolete warning.
warnings.simplefilter(action="ignore", category=UserWarning)
# Disable the HTTPS certificate verification warning.
disable_warnings()


def connect_field_path(path_a: str, path_b: str) -> str:
    return path_a + "." + path_b


class JiraClient:
    def __init__(self, url: str, access_token: str) -> None:
        self.jira = JIRA(
            server=url,
            token_auth=access_token,
            timeout=20,
            options={"verify": False},
        )
        self._field_cache: Dict[str, Dict[str, Union[str, List[str], bool]]] = {}

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

    def get_all_fields(self) -> "Dict[str, Dict[str, Union[str, List[str], bool]]]":
        if not self._field_cache:
            for field in self.jira.fields():
                if "schema" not in field.keys():
                    continue

                temp: Dict[str, Union[str, List[str], bool]] = {
                    "id": field["id"],
                    "isArray": False,
                }

                class FieldSchema(TypedDict):
                    type: str
                    items: NotRequired[str]

                schema: FieldSchema = field["schema"]

                if schema["type"] == "array":
                    temp["isArray"] = True
                    field_type_name = schema.get("items", None)
                else:
                    field_type_name = schema["type"]

                field_type: Optional[JiraFieldTypeDefinition] = get_jira_field_type(
                    field_type_name
                )

                path_list: List[str] = []
                if field_type is not None and field_type.get("isBasic", None) is False:
                    self._append_list(
                        path_list,
                        self._query_all_properties(field_type, field["id"]),
                    )
                else:
                    # Usually, the format is like below:
                    # "customfield_11005": {
                    #     "self": "https://jira_server/rest/api/2/customFieldOption/11005",
                    #     "value": "No",
                    #     "id": "11005",
                    #     "disabled": false
                    # },
                    path_list.append(connect_field_path(field["id"], "id"))
                    path_list.append(connect_field_path(field["id"], "value"))

                temp["path"] = path_list
                self._field_cache[field["name"]] = temp
        return self._field_cache

    def _query_all_properties(
        self,
        field_type: Optional[JiraFieldTypeDefinition],
        root_path: str,
    ) -> List[str]:
        path_list: List[str] = []

        if field_type is None:
            return path_list

        if field_type.get("isBasic", None) is True:
            self._append_str_to_list(path_list, field_type.get("name", ""))
        elif field_type.get("isArray", None) is True and "itemType" in field_type:
            item_field_type = get_jira_field_type(field_type["itemType"])
            if item_field_type is not None:
                self._append_list(
                    path_list,
                    self._query_all_properties(
                        item_field_type, item_field_type.get("name", "")
                    ),
                )
        elif "properties" in field_type:
            for child_field_type in field_type["properties"]:
                if (
                    child_field_type.get("isArray", None) is True
                    and "itemType" in child_field_type
                ):
                    child_field = get_jira_field_type(child_field_type["itemType"])
                else:
                    child_field = get_jira_field_type(child_field_type["type"])

                if child_field is not None:
                    new_root_path = connect_field_path(
                        root_path, child_field_type.get("name", "")
                    )

                    if child_field.get("isBasic") is True:
                        path_list.append(new_root_path)
                    elif (
                        child_field.get("isArray", None) is True
                        and "itemType" in child_field
                    ):
                        self._append_list(
                            path_list,
                            self._query_all_properties(
                                get_jira_field_type(child_field["itemType"]),
                                new_root_path,
                            ),
                        )
                    else:
                        self._append_list(
                            path_list,
                            self._query_all_properties(child_field, new_root_path),
                        )
        else:
            pass

        return path_list

    def _append_list(self, arr_a: List[str], arr_b: List[str]):
        for item in arr_b:
            arr_a.append(item)

    def _append_str_to_list(self, arr: List[str], statement: str):
        for i, _ in enumerate(arr):
            arr[i] = connect_field_path(arr[i], statement)

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
