from pathlib import Path
from typing import List

from jira_assistant.excel_definition import ExcelDefinition, ExcelDefinitionColumn
from jira_assistant.excel_operation import read_excel_file
from jira_assistant.priority import Priority
from jira_assistant.sprint_schedule import SprintScheduleStore
from jira_assistant.story import Story, StoryFactory


def mock_story_data() -> List[Story]:
    story_factory = StoryFactory(
        [
            ExcelDefinitionColumn(
                index=1,
                name="name",
                type=str,
                require_sort=False,
                sort_order=False,
                inline_weights=0,
                raise_ranking=0,
                scope_raise_ranking=0,
                scope_require_sort=False,
                scope_sort_order=True,
                jira_field_mapping=None,
            ),
            ExcelDefinitionColumn(
                index=2,
                name="regulatory",
                type=Priority,
                require_sort=False,
                sort_order=False,
                inline_weights=5,
                raise_ranking=0,
                scope_raise_ranking=0,
                scope_require_sort=False,
                scope_sort_order=True,
                jira_field_mapping=None,
            ),
            ExcelDefinitionColumn(
                index=3,
                name="partnerPriority",
                type=Priority,
                require_sort=False,
                sort_order=True,
                inline_weights=4,
                raise_ranking=0,
                scope_raise_ranking=0,
                scope_require_sort=False,
                scope_sort_order=True,
                jira_field_mapping=None,
            ),
            ExcelDefinitionColumn(
                index=4,
                name="productValue",
                type=Priority,
                require_sort=False,
                sort_order=True,
                inline_weights=3,
                raise_ranking=0,
                scope_raise_ranking=0,
                scope_require_sort=False,
                scope_sort_order=True,
                jira_field_mapping=None,
            ),
            ExcelDefinitionColumn(
                index=5,
                name="marketingUrgency",
                type=Priority,
                require_sort=False,
                sort_order=True,
                inline_weights=2,
                raise_ranking=0,
                scope_raise_ranking=0,
                scope_require_sort=False,
                scope_sort_order=True,
                jira_field_mapping=None,
            ),
            ExcelDefinitionColumn(
                index=6,
                name="revenue",
                type=Priority,
                require_sort=False,
                sort_order=True,
                inline_weights=1,
                raise_ranking=0,
                scope_raise_ranking=0,
                scope_require_sort=False,
                scope_sort_order=True,
                jira_field_mapping=None,
            ),
        ]
    )

    # NA, Middle, Middle, NA
    s_1 = story_factory.create_story()
    s_1["name"] = "s1"
    s_1["regulatory"] = Priority.NA
    s_1["partnerPriority"] = Priority.MIDDLE
    s_1["productValue"] = Priority.MIDDLE
    s_1["marketingUrgency"] = Priority.NA
    # NA, Low, High, NA
    s_2 = story_factory.create_story()
    s_2["name"] = "s2"
    s_2["regulatory"] = Priority.NA
    s_2["partnerPriority"] = Priority.LOW
    s_2["productValue"] = Priority.HIGH
    s_2["marketingUrgency"] = Priority.NA
    # NA, Middle, High, NA
    s_3 = story_factory.create_story()
    s_3["name"] = "s3"
    s_3["regulatory"] = Priority.NA
    s_3["partnerPriority"] = Priority.MIDDLE
    s_3["productValue"] = Priority.HIGH
    s_3["marketingUrgency"] = Priority.NA
    # NA, High, High, NA
    s_4 = story_factory.create_story()
    s_4["name"] = "s4"
    s_4["regulatory"] = Priority.NA
    s_4["partnerPriority"] = Priority.HIGH
    s_4["productValue"] = Priority.HIGH
    s_4["marketingUrgency"] = Priority.NA
    # High, NA, High, NA
    s_5 = story_factory.create_story()
    s_5["name"] = "s5"
    s_5["regulatory"] = Priority.HIGH
    s_5["partnerPriority"] = Priority.NA
    s_5["productValue"] = Priority.HIGH
    s_5["marketingUrgency"] = Priority.NA

    # Critical, N/A, Middle, N/A
    s_6 = story_factory.create_story()
    s_6["name"] = "s6"
    s_6["regulatory"] = Priority.CRITICAL
    s_6["partnerPriority"] = Priority.NA
    s_6["productValue"] = Priority.MIDDLE
    s_6["marketingUrgency"] = Priority.NA

    # Critical, N/A, High, Low
    s_7 = story_factory.create_story()
    s_7["name"] = "s7"
    s_7["regulatory"] = Priority.CRITICAL
    s_7["partnerPriority"] = Priority.NA
    s_7["productValue"] = Priority.HIGH
    s_7["marketingUrgency"] = Priority.LOW

    # Critical, Low, Middle, N/A
    s_8 = story_factory.create_story()
    s_8["name"] = "s8"
    s_8["regulatory"] = Priority.CRITICAL
    s_8["partnerPriority"] = Priority.LOW
    s_8["productValue"] = Priority.MIDDLE
    s_8["marketingUrgency"] = Priority.NA

    # Critical, Middle, High, Middle
    s_9 = story_factory.create_story()
    s_9["name"] = "s9"
    s_9["regulatory"] = Priority.CRITICAL
    s_9["partnerPriority"] = Priority.MIDDLE
    s_9["productValue"] = Priority.HIGH
    s_9["marketingUrgency"] = Priority.MIDDLE

    return [s_1, s_2, s_3, s_4, s_5, s_6, s_7, s_8, s_9]


def read_stories_from_excel(
    excel_file: Path, excel_definition_file: Path, sprint_schedule_file: Path
) -> List[Story]:
    excel_definition = ExcelDefinition()
    excel_definition.load_file(excel_definition_file)
    sprint_schedule = SprintScheduleStore()
    sprint_schedule.load_file(sprint_schedule_file)

    _, stories = read_excel_file(excel_file, excel_definition, sprint_schedule)

    return stories
