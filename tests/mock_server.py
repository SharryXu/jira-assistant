from re import IGNORECASE, search

from requests import Response
from requests_mock import Adapter
from requests_mock.request import _RequestObjectProxy
from requests_mock.response import create_response

mock_jira_stories = {
    "a-1": {"status": "CLOSED", "domain": "A"},
    "a-2": {"status": "PENDING", "domain": "A"},
    "a-3": {"status": "PENDING", "domain": "A"},
    "a-4": {"status": "PENDING", "domain": "A"},
    "b-1": {"status": "PENDING", "domain": "B"},
    "b-2": {"status": "PENDING", "domain": "B"},
    "c-1": {"status": "PENDING", "domain": "C"},
    "c-2": {"status": "PENDING", "domain": "C"},
}


def custom_matcher(request: _RequestObjectProxy) -> Response | None:
    if (
        search(pattern="rest/api/2/search", string=request.path, flags=IGNORECASE)
        is not None
    ):
        return mock_search_response(request)
    if (
        search(pattern="rest/api/2/field", string=request.path, flags=IGNORECASE)
        is not None
    ):
        return mock_field_response(request)
    if (
        search(pattern="rest/api/2/myself", string=request.path, flags=IGNORECASE)
        is not None
    ):
        return mock_myself_response(request)
    if (
        search(pattern="rest/api/2/serverinfo", string=request.path, flags=IGNORECASE)
        is not None
    ):
        return mock_server_info_response(request)
    return None


def mock_jira_requests() -> Adapter:
    adapter = Adapter(False)
    adapter.add_matcher(custom_matcher)  # type: ignore
    return adapter


def mock_server_info_response(request: _RequestObjectProxy) -> Response:
    return create_response(
        request=request,
        status_code=200,
        json={
            "baseUrl": "https://your_jira.com",
            "version": "8.20.13",
            "versionNumbers": [8, 20, 13],
            "deploymentType": "Server",
            "buildNumber": 820013,
            "buildDate": "2022-09-21T00:00:00.000-0700",
            "databaseBuildNumber": 820013,
            "serverTime": "2023-03-29T00:15:35.205-0700",
            "scmInfo": "e83256f8976830734d21b999890eb027cb94ffc2",
            "serverTitle": "YourJira",
        },
    )


def mock_myself_response(request: _RequestObjectProxy) -> Response:
    return create_response(
        request=request,
        status_code=200,
        json={
            "self": "https://your_jira.com/rest/api/2/user?username=sharry.xu",
            "key": "sharry.xu",
            "name": "sharry.xu",
            "emailAddress": "sharry.xu@company.com",
            "avatarUrls": {
                "48x48": "https://your_jira.com/secure/useravatar?ownerId=sharry.xu&avatarId=17002",
                "24x24": "https://your_jira.com/secure/useravatar?size=small&ownerId=sharry.xu&avatarId=17002",
                "16x16": "https://your_jira.com/secure/useravatar?size=xsmall&ownerId=sharry.xu&avatarId=17002",
                "32x32": "https://your_jira.com/secure/useravatar?size=medium&ownerId=sharry.xu&avatarId=17002",
            },
            "displayName": "Sharry Xu",
            "active": True,
            "deleted": False,
            "timeZone": "Asia/Shanghai",
            "locale": "en_US",
            "groups": {"size": 91, "items": []},
            "applicationRoles": {"size": 1, "items": []},
            "expand": "groups,applicationRoles",
        },
    )


def mock_search_response(request: _RequestObjectProxy) -> Response:
    story_ids = [
        story_id.strip("'")
        for story_id in request.qs["jql"][0]
        .split("in")[1]
        .strip()
        .strip("(")
        .strip(")")
        .split(",")
    ]

    response_json = {
        "expand": "names,schema",
        "startAt": 0,
        "maxResults": len(story_ids),
        "total": len(story_ids),
        "issues": [],
    }

    for story_id in story_ids:
        response_json["issues"].append(
            {
                "key": story_id,
                "fields": {
                    "customfield_15601": {
                        "value": mock_jira_stories[story_id]["domain"]
                    },
                    "status": {"name": mock_jira_stories[story_id]["status"]},
                },
            }
        )

    return create_response(request=request, status_code=200, json=response_json)


def mock_field_response(request: _RequestObjectProxy) -> Response:
    return create_response(
        request=request,
        status_code=200,
        json=[
            {
                "id": "status",
                "name": "Status",
                "custom": False,
                "orderable": False,
                "navigable": True,
                "searchable": True,
                "clauseNames": ["status"],
                "schema": {"type": "status", "system": "status"},
            },
            {
                "id": "customfield_15601",
                "name": "Domain",
                "custom": True,
                "orderable": True,
                "navigable": True,
                "searchable": True,
                "clauseNames": ["cf[15601]", "Domain"],
                "schema": {
                    "type": "option",
                    "custom": "com.atlassian.jira.plugin.system.customfieldtypes:select",
                    "customId": 15601,
                },
            },
        ],
    )
