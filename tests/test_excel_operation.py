import pathlib
from os import remove

from jira_assistant.excel_definition import ExcelDefinition
from jira_assistant.excel_operation import output_to_csv_file, read_excel_file
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

    def test_output_to_csv_file(self):
        excel_definition = ExcelDefinition()
        excel_definition.load_file(SRC_ASSETS / "excel_definition.json")
        sprint_schedule = SprintScheduleStore()
        sprint_schedule.load_file(SRC_ASSETS / "sprint_schedule.json")

        _, stories = read_excel_file(
            HERE / "files/happy_path.xlsx", excel_definition, sprint_schedule
        )

        output_to_csv_file(HERE / "files/happy_path.csv", stories)

        with open(HERE / "files/happy_path.csv", mode="r", encoding="utf-8") as file:
            assert "," in file.readline()

        remove(HERE / "files/happy_path.csv")
