import pathlib

from dotenv import load_dotenv

HERE = pathlib.Path(__file__).resolve().parent
SRC_ASSETS: pathlib.Path = HERE.parent / "src/jira_assistant/assets"


def pytest_configure(config):
    load_dotenv(SRC_ASSETS / ".env")
