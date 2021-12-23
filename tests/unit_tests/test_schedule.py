"""Unit tests for schedule.py
"""

import sys
sys.path.insert(0, './vstp')  # nopep8
import pytest
import schedule as sched


@pytest.fixture
def schedule():

    return sched.Schedule(**{
        'uid': 'A11111',
        'ssd': '1970-01-01',
        'train_status': '1',
        'train_category': 'OO',
        'headcode': '1A11',
        'service_code': '21755001',
        'power_type': 'EMU',
        'timing_load': '390',
        'speed': '125',
        'op_char': '',
        'seating': 'B',
        'sleepers': '',
        'reservations': ''

    })


class TestSchedule:
    def test_init(self, schedule):

        assert schedule.__class__.__name__ == 'Schedule'

    def test_end_date(self, schedule):

        assert str(schedule.end_date) == '1970-01-01'

    def test_days_run(self, schedule):

        assert schedule.days_run == '0001000'

    def test_format_date(self):

        dt = '1970-01-01'
        assert not sched.Schedule.format_date('')
        parsed = sched.Schedule.format_date(dt)
        assert str(parsed) == '1970-01-01 00:00:00'
        parsed = sched.Schedule.format_date(dt, date_only=True)
        assert str(parsed) == '1970-01-01'
