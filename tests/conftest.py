from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent


def pytest_configure(config):
    load_dotenv(HERE / "test.env")

    temp_folder: Path = HERE / "temp"

    if not temp_folder.exists():
        temp_folder.mkdir(parents=True, exist_ok=True)
