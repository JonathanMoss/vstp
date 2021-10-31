"""Tests for main.py"""

import builtins
import os
from unittest import mock
import pytest
import main
from network_links import NetworkLink
from location_record import LocationRecord


@pytest.fixture
def loc_records():

    return [
        'dummy',
        'dummy',
        'location_code',
        'location_name',
        'start_date',
        'end_date',
        '1',
        '2',
        'timing_point_type',
        'zone',
        'stanox_code',
        'off_network_indicator',
        'force_lpb'
    ]


@pytest.fixture
def nwk_records():

    ret_val = [
        [index for index in range(19)],
        [index for index in range(19)]
    ]

    ret_val[0][4] == 'BUS'

    return ret_val


class TestMain:

    def test_import_from_file(self):

        mock_open = mock.mock_open(read_data='line\tone\nline\ttwo\n')
        with mock.patch('builtins.open', mock_open):
            assert main.import_from_file('foo') == [
                ['line', 'one\n'],
                ['line', 'two\n']
            ]

    def test_import_location(self, monkeypatch, loc_records):

        with monkeypatch.context() as monkey:

            monkey.setattr(
                'main.import_from_file',
                lambda f_name: [loc_records]
            )

            locs = main.import_location()
            assert locs and isinstance(locs, list)
            assert locs[0].__class__.__name__ == 'LocationRecord'
            location_code = locs[0].location_code
            assert LocationRecord._instances[location_code]

    def test_import_network_links(self, monkeypatch, nwk_records):

        NetworkLink._instances = {}
        with monkeypatch.context() as monkey:

            monkey.setattr(
                'main.import_from_file',
                lambda f_name: nwk_records
            )

            nwks = main.import_network_links()
            assert nwks and isinstance(nwks, list)
            assert nwks[0].__class__.__name__ == 'NetworkLink'
            assert len(nwks[0]._instances) == 1
