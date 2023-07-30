"""Unit tests for network_links"""

# pylint: disable=C0301, E0401, C0413, W0621, R0903

import sys

sys.path.insert(0, './vstp/models')  # nopep8

import network_link as NWK
import pydantic
import pytest

TEST_FILE = './tests/files/bplan_nwk.raw'

@pytest.fixture
def get_test_file() -> list:
    """Returns the test file content as a list"""
    with open(TEST_FILE, 'r', encoding='utf-8') as file:
        return file.readlines()

@pytest.fixture
def nwk_instance():
    """Returns a NetworkLink instance"""
    line = 'NWK\tA\tKIDSGRV\tALSAGER\tML\t\t01-01-1995 00:00:00\t\tD\tD\t03882\tN\tY\tN\t5\tN\t\t0\t0'
    return NWK.NetworkLink.bplan_factory(line)


class TestEnv:
    """Tests testing environment"""
    def test_env(self, nwk_instance):
        """Test init"""
        assert isinstance(nwk_instance, NWK.NetworkLink)


class TestNetworkLink:
    """Unit tests for the networklink module"""
    def test_bplan_factory(self):
        """Tests the factory failure conditions"""
        assert NWK.NetworkLink.bplan_factory('     ') is None
        assert NWK.NetworkLink.bplan_factory('XXX\t' * 17) is None

        with pytest.raises(pydantic.ValidationError):
            assert NWK.NetworkLink.bplan_factory('XXX\t' * 18) is None

    def test_as_bplan(self, get_test_file):
        """Tests the as_bplan function"""
        for line in get_test_file:
            obj = NWK.NetworkLink.bplan_factory(line)
            assert isinstance(obj, NWK.NetworkLink)
            split_line = line.split('\t')
            split_obj = obj.as_bplan.split('\t')

            assert split_line[0] == split_obj[0]
            assert split_line[1] == split_obj[1]
            assert split_line[2] == split_obj[2]
            assert split_line[3] == split_obj[3]
            assert split_line[4].strip() == split_obj[4].strip()
            assert split_line[5] == split_obj[5]

            assert split_line[8] == split_obj[8]
            assert split_line[9] == split_obj[9]
            assert split_line[10] == split_obj[10]
            assert split_line[11] == split_obj[11]

            assert split_line[12] == split_obj[12]
            assert split_line[13] == split_obj[13]
            assert split_line[14] == split_obj[14]
            assert split_line[15] == split_obj[15]
            assert split_line[16].strip() == split_obj[16].strip()
            assert split_line[17] == split_obj[17]
            assert split_line[18].strip() == split_obj[18].strip()

            assert NWK.NetworkLink.bplan_factory(line).as_bplan == obj.as_bplan
