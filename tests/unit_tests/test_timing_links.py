"""Unit tests for timing links"""

# pylint: disable=C0301, E0401, C0413, W0621

import sys
sys.path.insert(0, './vstp') # nopep8
import timing_links as TLK
import pytest

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
        """test string stripping"""
        assert tlk_instance.origin == 'CREWE'
        assert tlk_instance.route_guage == None
