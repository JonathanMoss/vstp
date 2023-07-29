"""Unit tests for location.py"""

# pylint: disable=line-too-long, import-error, wrong-import-position
# pylint: disable=redefined-outer-name, wrong-import-order

import sys

import pytest

sys.path.insert(0, './vstp/models')  # nopep8
import location as LOC
from bng_latlon import OSGB36toWGS84 as conv

TEST_FILE = './tests/files/bplan_location.raw'

@pytest.fixture
def get_test_file() -> list:
    """Returns the test file content as a list"""
    with open(TEST_FILE, 'r', encoding='utf-8') as file:
        return file.readlines()


@pytest.fixture
def loc_instance():
    """Returns a Location instance"""
    line = 'LOC\tA\tABDVY  \tAberdovey\t01-01-1995 00:00:00\t\t260700\t296000\tO\t5\t64409\tN\t '
    return LOC.Location.bplan_factory(line)

@pytest.fixture
def distance_wgs():
    """Coordinates for testing distance calculations"""

    return {
        'thurso': conv(311300, 967900),
        'penzance': conv(147600, 30600)
    }

class TestLocation:
    """Unit tests for Location"""
    def test_init(self, loc_instance):
        """Test init"""
        obj = loc_instance.__class__.__name__
        assert obj == 'Location'

    def test_bng(self, loc_instance):
        """Test bng properties"""
        assert loc_instance.bng_coordinates == ('260700', '296000')

    def test_wgs(self, loc_instance):
        """Test wgs properties"""
        assert loc_instance.wgs_coordinates == (52.54398, -4.055593)

    def test_coord_are_valid(self, loc_instance):
        """Tests coordinate validation"""
        assert loc_instance.are_coords_valid
        loc_instance.easting = '999999'
        loc_instance.northing = '999999'
        assert not loc_instance.are_coords_valid

    def test_distance(self, distance_wgs):
        """Test distance calculations"""
        result = LOC.Location.distance(
            distance_wgs['thurso'],
            distance_wgs['penzance']
        )
        assert int(result) == 590

        result = LOC.Location.distance(
            distance_wgs['thurso'],
            distance_wgs['penzance'],
            miles=False
        )
        assert int(result) == 950442

    def test_as_bplan(self, get_test_file):
        """Process multiple LOC file entries"""
        for line in get_test_file:
            obj = LOC.Location.bplan_factory(line)
            assert isinstance(obj, LOC.Location)
            split_line = line.split('\t')
            split_obj = obj.as_bplan.split('\t')

            assert split_line[0] == split_obj[0]
            assert split_line[1] == split_obj[1]
            assert split_line[2] == split_obj[2]
            assert split_line[3] == split_obj[3]

            assert len(split_obj[4]) == 19
            assert len(split_obj[5]) == 19

            assert split_line[6] == split_obj[6] or split_obj[6] == ''
            assert split_line[7] == split_obj[7] or split_obj[7] == ''
            assert split_line[8] == split_obj[8]
            assert split_line[9] == split_obj[9]
            assert split_line[10] == split_obj[10]
            assert split_line[11] == split_obj[11]
            assert split_line[12] == split_obj[12]

            assert LOC.Location.bplan_factory(line).as_bplan == obj.as_bplan
