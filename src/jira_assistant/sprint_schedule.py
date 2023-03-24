import json
import pathlib
from pathlib import Path

__all__ = ["SprintScheduleStore"]


class SprintScheduleStore:
    def __init__(self) -> None:
        self.store: list[tuple] = []

    def load(self, content: str):
        """
        Load json string to generate the priority list

        :param content:
            JSON string content
        """
        if content is None:
            return

        try:
            raw_data = json.loads(content)

            priority = 0
            sprints = []
            for item in raw_data:
                for key, value in item.items():
                    if key.lower() in "priority":
                        priority = value
                    if key.lower() in "sprints":
                        for sprint in value:
                            if len(sprint) > 0:
                                sprints.append(sprint)

                for sprint in sprints:
                    self.store.append((sprint, priority))
                sprints.clear()
                priority = 0
        except Exception:
            raise ValueError(
                "The JSON structure of the sprint schedule file is wrong. Please check the documentation: https://github.com/SharryXu/jira-assistant"
            )

    def load_file(self, file: "str | Path"):
        """
        Load json file to generate the excel definition

        :param file:
            JSON file location
        """

        if file is None or not pathlib.Path(file).is_absolute():
            raise ValueError("The file is invalid.")

        if not pathlib.Path(file).exists():
            raise ValueError(f"The file is not exist. File: {file}")

        with open(file=file, mode="r") as schedule_file:
            try:
                self.load(schedule_file.read())
            finally:
                schedule_file.close()

    def get_priority(self, sprint: str) -> int:
        for item in self.store:
            if sprint.upper() in item[0].upper():
                return item[1]
        return 0

    def total_count(self):
        return len(self.store)
