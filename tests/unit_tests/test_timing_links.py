"""Unit tests for timing links"""

# pylint: disable=C0301, E0401, C0413, W0621

import sys
sys.path.insert(0, './vstp/models') # nopep8
import timing_link as TLK
import pytest

TEST_FILE = './tests/files/bplan_tlk.raw'


@pytest.fixture
def get_test_file() -> list:
    """Returns the test file content as a list"""
    with open(TEST_FILE, 'r', encoding='utf-8') as file:
        return file.readlines()
    
@pytest.fixture
def tlk_instance():
    """Returns a TimingLink object"""

    line = "TLK\tA\tCREWE  \tCREWBHJ\tFL \t2X86  \t1250 \t75 \t   \t-1 \t-1 \t24-05-1998 00:00:00\t\t+02'00\tThis is a description"
    return TLK.TimingLink.bplan_factory(line)

class TestTimingLink:
    """Tests for the TimingLink object"""

    def test_init(self, tlk_instance):
        """test initialisation"""
        obj = tlk_instance.__class__.__name__
        assert obj == 'TimingLink'

    def test_strip_strings(self, tlk_instance):
        """test string stripping/empty string parsing"""
        assert tlk_instance.origin == 'CREWE'
        assert tlk_instance.route_guage is None
        assert tlk_instance.speed == '75'

    def test_as_bplan(self, get_test_file):
        """Process multiple TLK file entries"""
        for line in get_test_file:
            obj = TLK.TimingLink.bplan_factory(line)
            assert isinstance(obj, TLK.TimingLink)
            split_line = line.split('\t')
            split_obj = obj.as_bplan.split('\t')

            assert split_line[0] == split_obj[0]
            assert split_line[1] == split_obj[1]
            assert split_line[2] == split_obj[2]
            assert split_line[3] == split_obj[3]
            assert split_line[4].strip() == split_obj[4].strip()
            assert split_line[5] == split_obj[5]
            assert split_line[6].strip() == split_obj[6].strip()
            assert split_line[7] == split_obj[7]
            assert split_line[8].split() == split_obj[8].split()
            assert split_line[9] == split_obj[9]
            assert split_line[10] == split_obj[10]

            assert split_line[13] == split_obj[13]
            assert TLK.TimingLink.bplan_factory(line).as_bplan == obj.as_bplan