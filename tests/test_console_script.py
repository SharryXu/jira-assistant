import pathlib
import subprocess
from os import environ, remove, walk

import pytest

HERE = pathlib.Path(__file__).resolve().parent


@pytest.mark.skipif(
    environ.get("JIRA_ACCESS_TOKEN") is None, reason="Security Consideration."
)
class TestConsoleScript:
    def test_process_excel_file(self):
        result = subprocess.run(
            ["sort-excel-file", HERE / "files/happy_path.xlsx"], capture_output=True
        )

        assert "happy_path_sorted.xlsx has been saved" in result.stdout.decode("utf-8")

        remove(HERE / "files/happy_path_sorted.xlsx")

    def test_generate_template(self):
        result = subprocess.run(
            ["generate-template", "excel-definition"], capture_output=True
        )

        assert "Generate success" in result.stdout.decode("utf-8")
        assert "excel-definition" in result.stdout.decode("utf-8")

    def teardown_method(self):
        for _, _, files in walk(pathlib.Path.cwd().absolute(), topdown=False):
            for file in files:
                if file.startswith("excel-definition") and "template" in file:
                    remove(file)
