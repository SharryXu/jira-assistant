import pathlib
from os import remove, walk
from subprocess import CalledProcessError, run

import pytest

HERE = pathlib.Path(__file__).resolve().parent


class TestConsoleScript:
    # Avoid call JIRA server.
    def test_process_excel_file(self):
        result = run(
            [
                "process-excel-file",
                HERE / "files/happy_path.xlsx",
                "--excel_definition_file",
                HERE / "files/excel_definition_avoid_jira_operations.json",
                "--sprint_schedule_file",
                HERE / "files/sprint_schedule.json",
            ],
            capture_output=True,
            check=True,
        )

        assert "xlsx has been saved" in result.stdout.decode("utf-8")

        remove(HERE / "files/happy_path_sorted.xlsx")

    def test_process_excel_file_using_invalid_definition_file(self):
        with pytest.raises(CalledProcessError):
            result = run(
                [
                    "process-excel-file",
                    HERE / "files/happy_path.xlsx",
                    "--excel_definition_file",
                    HERE / "files/excel_definition_invalid_structure.txt",
                ],
                capture_output=True,
                check=True,
            )

            assert "xlsx has been saved" in result.stdout.decode("utf-8")

    def test_generate_template_excel_definition(self):
        result = run(
            ["generate-template", "excel-definition"], capture_output=True, check=True
        )

        assert "Generate success" in result.stdout.decode("utf-8")
        assert "excel-definition" in result.stdout.decode("utf-8")

    def test_generate_template_excel(self):
        result = run(["generate-template", "excel"], capture_output=True, check=True)

        assert "Generate success" in result.stdout.decode("utf-8")
        assert "excel" in result.stdout.decode("utf-8")

    def test_generate_template_sprint_schedule(self):
        result = run(
            ["generate-template", "sprint-schedule"], capture_output=True, check=True
        )

        assert "Generate success" in result.stdout.decode("utf-8")
        assert "schedule" in result.stdout.decode("utf-8")

    def test_generate_template_failed(self):
        with pytest.raises(CalledProcessError):
            run(["generate-template", "abc"], capture_output=True, check=True)

    def test_update_jira_info(self):
        result = run(
            [
                "update-jira-info",
                "--access_token",
                "123456",
                "--url",
                "http://localhost",
            ],
            capture_output=True,
            check=True,
        )

        assert "Add/Update jira url success" in result.stdout.decode("utf-8")
        assert "Add/Update jira access token success" in result.stdout.decode("utf-8")

    def test_update_jira_info_failed(self):
        with pytest.raises(CalledProcessError):
            result = run(
                ["update-jira-info", "--access_token", " "],
                capture_output=True,
                check=True,
            )

            assert "Please check the access token" in result.stderr.decode("utf-8")

    def teardown_method(self):
        for _, _, files in walk(pathlib.Path.cwd().absolute(), topdown=False):
            for file in files:
                if file.startswith("excel-definition") and "template" in file:
                    remove(file)
                if file.startswith("excel-template"):
                    remove(file)
                if file.startswith("sprint-schedule"):
                    remove(file)
