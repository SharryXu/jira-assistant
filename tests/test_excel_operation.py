import pathlib
from os import environ, remove

import pytest

from jira_assistant.excel_definition import *
from jira_assistant.excel_operation import *
from jira_assistant.jira_client import *
from jira_assistant.sprint_schedule import *

HERE = pathlib.Path(__file__).resolve().parent
SRC_ASSETS: pathlib.Path = HERE.parent / "src/jira_assistant/assets"


class TestExcelOperation:
    @pytest.mark.skipif(
        environ.get("JIRA_ACCESS_TOKEN") is None, reason="Security Consideration."
    )
    def test_read_excel_file(self):
        excel_definition = ExcelDefinition()
        excel_definition.load_file(SRC_ASSETS / "excel_definition.json")
        sprint_schedule = SprintScheduleStore()
        sprint_schedule.load_file(SRC_ASSETS / "sprint_schedule.json")

        columns, stories = read_excel_file(
            HERE / "files/happy_path.xlsx", excel_definition, sprint_schedule
        )
        assert len(columns) == 24
        assert len(stories) == 8

    @pytest.mark.skipif(
        environ.get("JIRA_ACCESS_TOKEN") is None, reason="Security Consideration."
    )
    def test_process_excel_file(self):
        process_excel_file(
            HERE / "files/happy_path.xlsx",
            HERE / "files/happy_path_sorted.xlsx",
            excel_definition_file=str(SRC_ASSETS / "excel_definition.json"),
            sprint_schedule_file=str(SRC_ASSETS / "sprint_schedule.json"),
        )

        excel_definition = ExcelDefinition()
        excel_definition.load_file(SRC_ASSETS / "excel_definition.json")
        sprint_schedule = SprintScheduleStore()
        sprint_schedule.load_file(SRC_ASSETS / "sprint_schedule.json")

        _, stories = read_excel_file(
            HERE / "files/happy_path_sorted.xlsx", excel_definition, sprint_schedule
        )

        assert len(stories) == 8

        jira_client = JiraClient(environ["JIRA_URL"], environ["JIRA_ACCESS_TOKEN"])

        noneed_sort_statuses = [
            "SPRINT COMPLETE",
            "PENDING RELEASE",
            "PRODUCTION TESTING",
            "CLOSED",
        ]

        jira_fields = [
            {
                "name": "domain",
                "jira_name": "customfield_15601",
                "jira_path": "customfield_15601.value",
            },
            {"name": "status", "jira_name": "status", "jira_path": "status.name"},
        ]

        for i in range(len(stories) - 1):
            story_id_0 = stories[i]["storyId"].lower().strip()
            story_id_1 = stories[i + 1]["storyId"].lower().strip()
            query_result = jira_client.get_stories_detail(
                [story_id_0, story_id_1], jira_fields
            )
            if (
                query_result[story_id_0]["status"].upper() not in noneed_sort_statuses
                and query_result[story_id_1]["status"].upper()
                not in noneed_sort_statuses
            ):
                assert stories[i] >= stories[i + 1]

        remove(HERE / "files/happy_path_sorted.xlsx")
