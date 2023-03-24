import pathlib

from jira_assistant.sprint_schedule import *

HERE = pathlib.Path(__file__).resolve().parent
SRC_ASSETS = HERE.parent / "src/jira_assistant/assets"


class TestSprintSchedule:
    def test_load_sprint_schedule(self):
        schedule_filename = SRC_ASSETS / "sprint_schedule.json"
        store = SprintScheduleStore()
        store.load_file(schedule_filename)
        assert store.total_count() > 0

    def test_get_priority(self):
        schedule_filename = SRC_ASSETS / "sprint_schedule.json"
        store = SprintScheduleStore()
        assert store.get_priority("R138") == 0

        store.load_file(schedule_filename)
        assert store.get_priority("R140") == 2
