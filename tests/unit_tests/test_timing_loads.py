"""Unit tests for timing links"""

# pylint: disable=C0301, E0401, C0413, W0621

import sys
sys.path.insert(0, './vstp/models') # nopep8
import timing_load as TLD
import pytest

@pytest.fixture
def tld_instance():
    """Returns a TimingLoad object"""

    line = "TLD\tA\t37    \t350  \t50 \t   \tClass 37 & 10 coaches & Steam loco (50 mph)\tD  \t350 \t50 "
    return TLD.TimingLoad.bplan_factory(line)

class TestTimingLink:
    """Tests for the TimingLink object"""

    def test_init(self, tld_instance):
        """test initialisation"""
        obj = tld_instance.__class__.__name__
        assert obj == 'TimingLoad'

    def test_strip_strings(self, tld_instance):
        """test string stripping/empty string parsing"""
        assert tld_instance.traction_type == '37'
        assert tld_instance.ra_guage is None
        assert tld_instance.max_speed == '50'
