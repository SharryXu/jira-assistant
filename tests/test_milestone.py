import pathlib

from jira_assistant.milestone import Milestone
from jira_assistant.sprint_schedule import *

HERE = pathlib.Path(__file__).resolve().parent
SRC_ASSETS = HERE.parent / "src/jira_assistant/assets"


class TestMilestone:
    def test_init(self):
        schedule_filename = SRC_ASSETS / "sprint_schedule.json"
        store = SprintScheduleStore()
        store.load_file(schedule_filename)

        milestone = Milestone("R139")
        milestone.calc_priority(store)
        assert milestone.priority == 1

    def test_compare(self):
        schedule_filename = SRC_ASSETS / "sprint_schedule.json"
        store = SprintScheduleStore()
        store.load_file(schedule_filename)

        m1 = Milestone("M123")
        m1.calc_priority(store)
        m2 = Milestone("M125")
        m2.calc_priority(store)
        m3 = Milestone("m125")
        m3.calc_priority(store)
        m4 = Milestone("R141")
        m4.calc_priority(store)
        assert m1 < m2
        assert m2 == m3
        assert m3 == m4
