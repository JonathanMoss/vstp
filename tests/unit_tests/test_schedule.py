"""Unit tests for schedule.py
"""

# pylint: disable=C0301, C0413, E1101, C0116, C0115, W0621, R0201, C0103

import sys
sys.path.insert(0, './vstp')  # nopep8
import pytest
import schedule as sched


@pytest.fixture
def location_term():

    return sched.LocationTerminating(**{
        'tiploc': 'CREWE',
        'suffix': '1',
        'wta': '1400H',
        'pta': '1402',
        'plt': '7',
        'path': 'DSL',
        'act': 'TF'
    })


@pytest.fixture
def location_interm():

    return sched.LocationIntermediate(**{
        'tiploc': 'CREWE',
        'suffix': '1',
        'wtp': '1200H',
        'plt': '4',
        'line': 'UFL',
        'eng_all': '1H',
        'pathing_all': 'H',
        'perf_all': '2H',
        'act': ''
    })


@pytest.fixture
def basic_schedule():

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


@pytest.fixture
def extra_schedule():

    return sched.ExtraSchedule(**{
        'uic': '',
        'atoc': 'SR',
        'appl': 'Y'
    })


@pytest.fixture
def location_origin():

    return sched.LocationOrigin(**{
        'tiploc': 'CREWE',
        'suffix': '1',
        'wtd': '1200H',
        'ptd': '1159',
        'plt': '4',
        'line': 'UFL',
        'eng_all': '1H',
        'pathing_all': 'H',
        'perf_all': '2H',
        'act': 'TB'
    })


def test_extrapolate_allowance():

    assert sched.extrapolate_allowance('1H') == 90
    assert sched.extrapolate_allowance('9H') == 570
    assert sched.extrapolate_allowance('1') == 60
    assert sched.extrapolate_allowance('H') == 30
    assert sched.extrapolate_allowance('19') == 1140
    assert sched.extrapolate_allowance(' ') == 0
    assert sched.extrapolate_allowance('') == 0
    assert sched.extrapolate_allowance('123') == 0


class TestBasicSchedule:

    def test_init(self, basic_schedule):

        assert basic_schedule.__class__.__name__ == 'BasicSchedule'
        assert str(
            basic_schedule) == 'BSN99999 7001017001010001000 1OO9X990900199999999 D  9999125Q     B            N'

    def test_end_date(self, basic_schedule):

        assert str(basic_schedule.date_to) == '1970-01-01'

    def test_days_run(self, basic_schedule):

        assert basic_schedule.days_run == '0001000'

    def test_format_date(self):

        dt = '1970-01-01'
        assert not sched.format_date('')
        parsed = sched.format_date(dt)
        assert str(parsed) == '1970-01-01 00:00:00'
        parsed = sched.format_date(dt, date_only=True)
        assert str(parsed) == '1970-01-01'

    def test_create_from_string(self):

        bs = 'BSRG828851510191510231100100 POO2N75    113575825 DMUE   090      S            O'
        res = sched.BasicSchedule.create_from_string(bs)
        assert str(res) == bs


class TestExtraSchedule:

    def test_init(self, extra_schedule):

        assert extra_schedule.__class__.__name__ == 'ExtraSchedule'
        assert str(
            extra_schedule) == 'BX         SRY                                                                  '

    def test_create_from_string(self):

        bx = 'BX         SRY                                                                  '
        res = sched.ExtraSchedule.create_from_string(bx)
        assert str(res) == bx

        with pytest.raises(ValueError):
            sched.ExtraSchedule.create_from_string(None)
            sched.ExtraSchedule.create_from_string(f'BS{bx[2:]}')
            sched.ExtraSchedule.create_from_string(bx[2:])


class TestLocationOrigin:

    def test_init(self, location_origin):

        assert location_origin.__class__.__name__ == 'LocationOrigin'
        assert str(
            location_origin) == 'LOCREWE  11200H11594  UFL1HH TB          2H                                     '

    def test_create_from_string(self):

        lo = 'LOGLGQHL  1703 17033  UEG    TB                                                 '
        res = sched.LocationOrigin.create_from_string(lo)
        assert str(res) == lo


class TestLocationIntermediate:

    def test_init(self, location_interm):

        assert location_interm.__class__.__name__ == 'LocationIntermediate'
        assert str(
            location_interm).startswith('LICREWE  1          1200H        4  UFL               1HH 2H')

    def test_create_from_string(self):

        li = 'LILENZIE  1714 1714H     17141714         T                                     '
        res = sched.LocationIntermediate.create_from_string(li)
        assert str(res) == li


class TestLocationTerminating:

    def test_init(self, location_term):

        assert location_term.__class__.__name__ == 'LocationTerminating'
        assert str(location_term).startswith('LTCREWE  11400H14027  DSLTF')

    def test_create_from_string(self):

        lt = 'LTFALKRKG 1734 17341     TF                                                     '
        res = sched.LocationTerminating.create_from_string(lt)
        assert str(res) == lt
