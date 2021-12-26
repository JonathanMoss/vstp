"""Unit tests for schedule.py
"""

import sys
sys.path.insert(0, './vstp')  # nopep8
import pytest
import schedule as sched


@pytest.fixture
def schedule():

    return sched.BasicSchedule(**{
        'uid': '',
        'date_from': '1970-01-01',
        'train_status': '1',
        'train_category': 'OO',
        'train_identity': '',
        'service_code': '',
        'power_type': '',
        'timing_load': '',
        'speed': '125',
        'op_char': '',
        'seating': 'B',
        'sleepers': '',
        'reservations': '',
        'headcode': '0900'

    })


class TestBasicSchedule:
    def test_init(self, schedule):

        assert schedule.__class__.__name__ == 'BasicSchedule'
        assert str(
            schedule) == 'BSN99999 7001017001010001000 1OO9X990900199999999 D  9999125Q     B            N'

    def test_end_date(self, schedule):

        assert str(schedule.date_to) == '1970-01-01'

    def test_days_run(self, schedule):

        assert schedule.days_run == '0001000'

    def test_format_date(self):

        dt = '1970-01-01'
        assert not sched.Schedule.format_date('')
        parsed = sched.Schedule.format_date(dt)
        assert str(parsed) == '1970-01-01 00:00:00'
        parsed = sched.Schedule.format_date(dt, date_only=True)
        assert str(parsed) == '1970-01-01'

    def test_create_from_string(self):

        bs = 'BSRG828851510191510231100100 POO2N75    113575825 DMUE   090      S            O'
        res = sched.BasicSchedule.create_from_string(bs)
        # assert res.date_from == ''
        assert str(res) == ''

        # BSRG828851510191510231100100 POO2N75    113575825 DMUE   090      S            O
        # BSRG828851510191510231100100 POO2N75    113575825 DMUE   090      S           O
