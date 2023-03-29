import pathlib

from dotenv import load_dotenv

HERE = pathlib.Path(__file__).resolve().parent


def pytest_configure(config):
    load_dotenv(HERE / "test.env")
