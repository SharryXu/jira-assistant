from jira_assistant.excel_definition import ExcelDefinitionColumn
from jira_assistant.priority import Priority
from jira_assistant.story import *


def mock_data() -> list:
    storyFactory = StoryFactory(
        [
            ExcelDefinitionColumn(
                index=1,
                name="name",
                type=str,
                require_sort=False,
                sort_order=False,
                inline_weights=0,
                raise_ranking=0,
                raise_ranking_level_scope_index=[],
            ),
            ExcelDefinitionColumn(
                index=2,
                name="regulatory",
                type=Priority,
                require_sort=False,
                sort_order=False,
                inline_weights=5,
                raise_ranking=0,
                raise_ranking_level_scope_index=[],
            ),
            ExcelDefinitionColumn(
                index=3,
                name="partnerPriority",
                type=Priority,
                require_sort=False,
                sort_order=True,
                inline_weights=4,
                raise_ranking=0,
                raise_ranking_level_scope_index=[],
            ),
            ExcelDefinitionColumn(
                index=4,
                name="productValue",
                type=Priority,
                require_sort=False,
                sort_order=True,
                inline_weights=3,
                raise_ranking=0,
                raise_ranking_level_scope_index=[],
            ),
            ExcelDefinitionColumn(
                index=5,
                name="marketingUrgency",
                type=Priority,
                require_sort=False,
                sort_order=True,
                inline_weights=2,
                raise_ranking=0,
                raise_ranking_level_scope_index=[],
            ),
            ExcelDefinitionColumn(
                index=6,
                name="revenue",
                type=Priority,
                require_sort=False,
                sort_order=True,
                inline_weights=1,
                raise_ranking=0,
                raise_ranking_level_scope_index=[],
            ),
        ]
    )

    # NA, Middle, Middle, NA
    s1 = storyFactory.create_story()
    s1["name"] = "s1"
    s1["regulatory"] = Priority.NA
    s1["partnerPriority"] = Priority.MIDDLE
    s1["productValue"] = Priority.MIDDLE
    s1["marketingUrgency"] = Priority.NA
    # NA, Low, High, NA
    s2 = storyFactory.create_story()
    s2["name"] = "s2"
    s2["regulatory"] = Priority.NA
    s2["partnerPriority"] = Priority.LOW
    s2["productValue"] = Priority.HIGH
    s2["marketingUrgency"] = Priority.NA
    # NA, Middle, High, NA
    s3 = storyFactory.create_story()
    s3["name"] = "s3"
    s3["regulatory"] = Priority.NA
    s3["partnerPriority"] = Priority.MIDDLE
    s3["productValue"] = Priority.HIGH
    s3["marketingUrgency"] = Priority.NA
    # NA, High, High, NA
    s4 = storyFactory.create_story()
    s4["name"] = "s4"
    s4["regulatory"] = Priority.NA
    s4["partnerPriority"] = Priority.HIGH
    s4["productValue"] = Priority.HIGH
    s4["marketingUrgency"] = Priority.NA
    # High, NA, High, NA
    s5 = storyFactory.create_story()
    s5["name"] = "s5"
    s5["regulatory"] = Priority.HIGH
    s5["partnerPriority"] = Priority.NA
    s5["productValue"] = Priority.HIGH
    s5["marketingUrgency"] = Priority.NA

    # Critical, N/A, Middle, N/A
    s6 = storyFactory.create_story()
    s6["name"] = "s6"
    s6["regulatory"] = Priority.CRITICAL
    s6["partnerPriority"] = Priority.NA
    s6["productValue"] = Priority.MIDDLE
    s6["marketingUrgency"] = Priority.NA

    # Critical, N/A, High, Low
    s7 = storyFactory.create_story()
    s7["name"] = "s7"
    s7["regulatory"] = Priority.CRITICAL
    s7["partnerPriority"] = Priority.NA
    s7["productValue"] = Priority.HIGH
    s7["marketingUrgency"] = Priority.LOW

    # Critical, Low, Middle, N/A
    s8 = storyFactory.create_story()
    s8["name"] = "s8"
    s8["regulatory"] = Priority.CRITICAL
    s8["partnerPriority"] = Priority.LOW
    s8["productValue"] = Priority.MIDDLE
    s8["marketingUrgency"] = Priority.NA

    # Critical, Middle, High, Middle
    s9 = storyFactory.create_story()
    s9["name"] = "s9"
    s9["regulatory"] = Priority.CRITICAL
    s9["partnerPriority"] = Priority.MIDDLE
    s9["productValue"] = Priority.HIGH
    s9["marketingUrgency"] = Priority.MIDDLE

    return [s1, s2, s3, s4, s5, s6, s7, s8, s9]


class TestStory:
    def test_compare_story(self):
        data = mock_data()
        s1 = data[0]
        s2 = data[1]
        s3 = data[2]
        s4 = data[3]
        s5 = data[4]
        s6 = data[5]
        s7 = data[6]
        s8 = data[7]
        s9 = data[8]
        assert s1 < s2
        assert s1 < s3
        assert s2 < s3
        assert s3 < s5
        assert s2 < s5
        assert s4 < s5
        assert s1 < s5
        assert s6 < s7
        assert s8 < s9

    def test_compare_story_property(self):
        data = mock_data()
        s8 = data[7]
        s9 = data[8]
        assert s8["name"] < s9["name"]
        assert s8["productValue"] < s9["productValue"]

    def test_sort_stories_by_property_and_order(self):
        data = mock_data()

        stories = sorted(data, reverse=False)

        for i in range(len(stories) - 1):
            assert stories[i] <= stories[i + 1]
