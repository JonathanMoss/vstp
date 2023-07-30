"""Unit tests for timing links"""

# pylint: disable=C0301, E0401, C0413, W0621

import sys
sys.path.insert(0, './vstp/models') # nopep8
import timing_load as TLD
import pytest

TEST_FILE = './tests/files/bplan_tld.raw'

@pytest.fixture
def get_test_file() -> list:
    """Returns the test file content as a list"""
    with open(TEST_FILE, 'r', encoding='utf-8') as file:
        return file.readlines()

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

    def test_as_bplan(self, get_test_file):
        """Process multiple TLD file entries"""
        for line in get_test_file:
            obj = TLD.TimingLoad.bplan_factory(line)
            assert isinstance(obj, TLD.TimingLoad)
            split_line = line.split('\t')
            split_obj = obj.as_bplan.split('\t')

            assert split_line[0] == split_obj[0]
            assert split_line[1] == split_obj[1]
            assert split_line[2] == split_obj[2]
            assert split_line[3].strip() == split_obj[3].strip()
            assert split_line[4].strip() == split_obj[4].strip()
            assert split_line[5].strip() == split_obj[5].strip()
            assert split_line[6] == split_obj[6]
            assert split_line[7].strip() == split_obj[7].strip()
            assert split_line[8].strip() == split_obj[8].strip()
            assert split_line[9].strip() == split_obj[9].strip()

            assert TLD.TimingLoad.bplan_factory(line).as_bplan == obj.as_bplan
