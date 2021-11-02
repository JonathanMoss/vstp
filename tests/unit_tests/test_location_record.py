"""Unit tests for location_record
"""
import sys
sys.path.insert(0, './vstp')  # nopep8
import pytest
import json
import location_record as LOC


@pytest.fixture
def record_from_file():

    record = 'LOC\tA\tKIDSGRV\tKidsgrove\t01-01-1995 00:00:00\t01-01-1995 00:00:00\t383700\t354300\tM\t5\t43031\tN\t'
    return LOC.LocationRecord(*record.split('\t'))


class TestEnv:
    def test_env(self):
        assert hasattr(LOC, 'EAST_L')
        assert hasattr(LOC, 'EAST_U')
        assert hasattr(LOC, 'NORTH_L')
        assert hasattr(LOC, 'NORTH_U')
        assert isinstance(LOC.LocationRecord._instances, dict)


class TestLocationRecord:
    def test_init(self, record_from_file):
        assert record_from_file.__class__.__name__ == 'LocationRecord'

    def test_as_dict(self, record_from_file):
        assert record_from_file.as_dict == {
            'easting/northing': (383700, 354300),
            'end_date': '01-01-1995 00:00:00',
            'force_lpb': '',
            'lat/lon': (53.08566483961731, -2.2448107258158285),
            'location_code': 'KIDSGRV',
            'location_name': 'Kidsgrove',
            'off_network_indicator': 'N',
            'stanox': '43031',
            'start_date': '01-01-1995 00:00:00',
            'timing_point_type': 'M',
            'zone': '5'
        }

    def test_repr(self, record_from_file):

        assert json.loads(str(record_from_file)) == {
            'easting/northing': [383700, 354300],
            'end_date': '01-01-1995 00:00:00',
            'force_lpb': '',
            'lat/lon': [53.08566483961731, -2.2448107258158285],
            'location_code': 'KIDSGRV',
            'location_name': 'Kidsgrove',
            'off_network_indicator': 'N',
            'stanox': '43031',
            'start_date': '01-01-1995 00:00:00',
            'timing_point_type': 'M',
            'zone': '5'
        }

    def test_distance(self):

        kidsgrove = (53.08566483961731, -2.2448107258158285)
        crewe = (53.089561, -2.433622)

        distance = LOC.LocationRecord.distance(
            kidsgrove, crewe
        )

        assert round(distance, 2) == 7.84

    def test_return_instance(self):

        assert LOC.LocationRecord.return_instance('KIDSGRV').__class__.__name__ == 'LocationRecord'

    def test_valid_coord(self):

        _type = 'northing'
        coord = LOC.NORTH_L - 1
        assert not LOC.LocationRecord.valid_coord(coord, _type)
        coord = LOC.NORTH_L
        assert LOC.LocationRecord.valid_coord(coord, _type)
        coord = LOC.NORTH_U + 1
        assert not LOC.LocationRecord.valid_coord(coord, _type)
        coord = LOC.NORTH_U
        assert LOC.LocationRecord.valid_coord(coord, _type)

        _type = 'easting'
        coord = LOC.EAST_L - 1
        assert not LOC.LocationRecord.valid_coord(coord, _type)
        coord = LOC.EAST_L
        assert LOC.LocationRecord.valid_coord(coord, _type)
        coord = LOC.EAST_U + 1
        assert not LOC.LocationRecord.valid_coord(coord, _type)
        coord = LOC.EAST_U
        assert LOC.LocationRecord.valid_coord(coord, _type)

    def test_bng_coordinates(self, record_from_file):

        assert record_from_file.bng_coordinates == (383700, 354300)

    def test_wgs_coordinates(self, record_from_file):

        assert record_from_file.wgs_coordinates == (53.08566483961731, -2.2448107258158285)
