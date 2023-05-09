from __future__ import annotations

from pathlib import Path
from sys import version_info
from typing import List, TypedDict, Union

if version_info < (3, 11):
    from typing_extensions import NotRequired, Self
else:
    from typing import NotRequired, Self


def is_absolute_path_valid(path: Union[str, Path]) -> bool:
    if path is None or not Path(path).is_absolute() or not Path(path).exists():
        return False
    return True


class JiraFieldTypeDefinition(TypedDict):
    type: str
    name: NotRequired[str]
    properties: NotRequired[List[Self]]
    isBasic: NotRequired[bool]
    isArray: NotRequired[bool]
    itemType: NotRequired[str]


_jira_field_types: List[JiraFieldTypeDefinition] = [
    {
        "type": "any",
        "isBasic": True,
        "isArray": False,
    },
    {
        "type": "array",
        "isBasic": False,
        "isArray": True,
    },
    {
        "type": "date",
        "isBasic": True,
        "isArray": False,
    },
    {
        "type": "datetime",
        "isBasic": True,
        "isArray": False,
    },
    {
        "type": "string",
        "isBasic": True,
        "isArray": False,
    },
    {
        "type": "number",
        "isBasic": True,
        "isArray": False,
    },
    {
        "type": "user",
        "properties": [
            {"name": "name", "type": "string"},
            {"name": "emailAddress", "type": "string"},
            {"name": "displayName", "type": "string"},
        ],
        "isBasic": False,
        "isArray": False,
    },
    {
        "type": "securitylevel",
        "properties": [{"name": "name", "type": "string"}],
        "isBasic": False,
        "isArray": False,
    },
    {
        "type": "priority",
        "properties": [{"name": "name", "type": "string"}],
        "isBasic": False,
        "isArray": False,
    },
    {
        "type": "watches",
        "properties": [{"name": "watchCount", "type": "number"}],
        "isBasic": False,
        "isArray": False,
    },
    {
        "type": "comments-page",
        "properties": [
            {
                "name": "comments",
                "itemType": "comment",
                "type": "array",
                "isArray": True,
            }
        ],
        "isArray": False,
        "isBasic": False,
    },
    {
        "type": "comment",
        "properties": [
            {"name": "author", "type": "author"},
            {"name": "id", "type": "string"},
            {"name": "body", "type": "string"},
            {"name": "created", "type": "datetime"},
        ],
        "isBasic": False,
        "isArray": False,
    },
    {
        "type": "author",
        "properties": [
            {"name": "name", "type": "string"},
            {"name": "emailAddress", "type": "string"},
        ],
        "isBasic": False,
        "isArray": False,
    },
    {
        "type": "status",
        "properties": [
            {"name": "name", "type": "string"},
            {"name": "statusCategory", "type": "statusCategory"},
        ],
        "isBasic": False,
        "isArray": False,
    },
    {
        "type": "statusCategory",
        "properties": [
            {"name": "key", "type": "string"},
            {"name": "name", "type": "string"},
        ],
        "isArray": False,
        "isBasic": False,
    },
    {
        "type": "progress",
        "properties": [
            {"name": "progress", "type": "number"},
            {"name": "total", "type": "number"},
        ],
        "isBasic": False,
        "isArray": False,
    },
    {
        "type": "timetracking",
        "properties": [
            {"name": "timeSpent", "type": "string"},
            {"name": "timeSpentSeconds", "type": "number"},
            {"name": "remainingEstimate", "type": "string"},
            {"name": "remainingEstimateSeconds", "type": "number"},
        ],
        "isBasic": False,
        "isArray": False,
    },
    {
        "type": "option",
        "properties": [{"name": "value", "type": "string"}],
        "isBasic": False,
        "isArray": False,
    },
    {
        "type": "resolution",
        "properties": [
            {"name": "description", "type": "string"},
            {"name": "name", "type": "string"},
        ],
        "isBasic": False,
        "isArray": False,
    },
    {
        "type": "issuetype",
        "properties": [
            {"name": "description", "type": "string"},
            {"name": "name", "type": "string"},
        ],
        "isBasic": False,
        "isArray": False,
    },
    {
        "type": "project",
        "properties": [
            {"name": "name", "type": "string"},
            {"name": "key", "type": "string"},
            {"name": "projectTypeKey", "type": "string"},
            {"name": "projectCategory", "type": "projectCategory"},
        ],
        "isBasic": False,
        "isArray": False,
    },
    {
        "type": "projectCategory",
        "properties": [
            {"name": "description", "type": "string"},
            {"name": "name", "type": "string"},
        ],
        "isBasic": False,
        "isArray": False,
    },
    {"type": "issuelinks", "itemType": "issuelink", "isArray": True, "isBasic": False},
    {
        "type": "issuelink",
        "properties": [{"name": "id", "type": "string"}],
        "isBasic": False,
        "isArray": False,
    },
]


def get_jira_field_type(type_name: str | None) -> JiraFieldTypeDefinition | None:
    if type_name is None:
        return None
    for field_type in _jira_field_types:
        if field_type["type"].lower() == type_name.lower():
            return field_type
    return None
