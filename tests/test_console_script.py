import pathlib
from os import remove, walk
from subprocess import run

import pytest
from mock_server import mock_jira_requests
from requests_mock import Mocker

HERE = pathlib.Path(__file__).resolve().parent


class TestConsoleScript:
    @pytest.mark.skipif(
        not (HERE.parent.parent / "assets/.env").exists(),
        reason="Only local machine can run.",
    )
    def test_process_excel_file(self):
        with Mocker(
            real_http=False, case_sensitive=False, adapter=mock_jira_requests()
        ):
            result = run(
                ["process-excel-file", HERE / "files/happy_path.xlsx"],
                capture_output=True,
                check=True,
            )

            assert "xlsx has been saved" in result.stdout.decode("utf-8")

            remove(HERE / "files/happy_path_sorted.xlsx")

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

    def teardown_method(self):
        for _, _, files in walk(pathlib.Path.cwd().absolute(), topdown=False):
            for file in files:
                if file.startswith("excel-definition") and "template" in file:
                    remove(file)
                if file.startswith("excel-template"):
                    remove(file)
