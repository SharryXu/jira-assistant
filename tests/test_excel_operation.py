import pathlib
from os import remove

from utils import read_stories_from_excel

from jira_assistant.excel_definition import ExcelDefinition
from jira_assistant.excel_operation import output_to_excel_file, read_excel_file
from jira_assistant.sprint_schedule import SprintScheduleStore

HERE = pathlib.Path(__file__).resolve().parent
SRC_ASSETS: pathlib.Path = HERE.parent / "src/jira_assistant/assets"


class TestExcelOperation:
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

    def test_output_to_excel_file(self):
        stories = read_stories_from_excel(
            HERE / "files/happy_path.xlsx",
            SRC_ASSETS / "excel_definition.json",
            SRC_ASSETS / "sprint_schedule.json",
        )

        output_to_excel_file(
            HERE / "files/happy_path_direct_output.xlsx",
            stories,
            ExcelDefinition().load_file(SRC_ASSETS / "excel_definition.json"),
        )

        assert (HERE / "files/happy_path_direct_output.xlsx").exists()

        remove(HERE / "files/happy_path_direct_output.xlsx")
