"""Unit tests for network_links"""
import sys
sys.path.insert(0, './vstp')  # nopep8
import json
import pytest
import network_links as NWK


@pytest.fixture
def nwk_instance():

    line = 'NWK\tA\tKIDSGRV\tALSAGER\tML\t\t01-01-1995 00:00:00\t\tD\tD\t03882\tN\tY\tN\t5\tN\t\t\t0'
    return NWK.NetworkLink(*line.split('\t'))


class TestEnv:
    def test_env(self):
        assert isinstance(NWK.NetworkLink._instances, dict)


class TestNetworkLink:
    def test_init(self, nwk_instance):
        assert nwk_instance.__class__.__name__ == 'NetworkLink'

    def test_return_instance(self, nwk_instance):
        NWK.NetworkLink.append_to_instance(nwk_instance)
        assert NWK.NetworkLink.return_instance('KIDSGRV')

    def test_as_dict(self, nwk_instance):

        as_dict = nwk_instance.as_dict
        assert as_dict == {
            'destination_location': 'ALSAGER',
            'distance': '03882',
            'doo_np': 'Y',
            'doo_p': 'N',
            'end_date': '',
            'final_direction': 'D',
            'initial_direction': 'D',
            'max_len': '0',
            'origin_location': 'KIDSGRV',
            'power': '',
            'ra': '',
            'retb': 'N',
            'reversable': 'N',
            'running_line_code': 'ML',
            'running_line_description': '',
            'start_date': '01-01-1995 00:00:00',
            'zone': '5'
        }

    def test_repr(self, nwk_instance):
        assert json.loads(str(nwk_instance)) == {
            'destination_location': 'ALSAGER',
            'distance': '03882',
            'doo_np': 'Y',
            'doo_p': 'N',
            'end_date': '',
            'final_direction': 'D',
            'initial_direction': 'D',
            'max_len': '0',
            'origin_location': 'KIDSGRV',
            'power': '',
            'ra': '',
            'retb': 'N',
            'reversable': 'N',
            'running_line_code': 'ML',
            'running_line_description': '',
            'start_date': '01-01-1995 00:00:00',
            'zone': '5'
        }

    def test_append_to_instance(self, nwk_instance):
        NWK.NetworkLink._instances = {}
        NWK.NetworkLink.append_to_instance(nwk_instance)
        assert 'KIDSGRV' in NWK.NetworkLink._instances
        assert len(NWK.NetworkLink._instances['KIDSGRV']) == 1

    def test_distance(self):
        assert NWK.NetworkLink.distance('KIDSGRV', 'ALSAGER') == 3882
        assert not NWK.NetworkLink.distance('KIDSGRV', 'CREWE')
        assert not NWK.NetworkLink.distance('CREWE', 'ALSAGER')

    def test_reversable_data(self):
        assert NWK.NetworkLink.reversable_data('KIDSGRV', 'ALSAGER') == {
            'final_direction': 'D',
            'inital_direction': 'D',
            'reversable': 'N'
        }

    def test_get_neighbours(self):
        assert NWK.NetworkLink.get_neighbours('KIDSGRV') == ['ALSAGER']

    def test_is_valid_tiploc(self):
        assert NWK.NetworkLink.is_valid_tiploc('KIDSGRV')
        assert not NWK.NetworkLink.is_valid_tiploc('FOO')
