"""Unit tests for location.py"""

# pylint: disable=line-too-long, import-error, wrong-import-position
# pylint: disable=redefined-outer-name, wrong-import-order

import pytest
import sys
sys.path.insert(0, './vstp/models')  # nopep8
import location as LOC
from bng_latlon import OSGB36toWGS84 as conv

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

    def test_geo_info(self, loc_instance):
        """Tests geolocation information lookup"""
        geo_info = loc_instance.geo_info
        assert geo_info.__class__.__name__ == 'GeocodeFarmReverse'
        assert 'postal' in geo_info.json
        assert geo_info.json['address'] == 'Rhos Dyfi, LL35 0RT, Wales, United Kingdom, United Kingdom'

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
