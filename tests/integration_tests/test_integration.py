"""Integration tests for the application"""

import main as Main
from pathfinder import Pathfinder
from location_record import LocationRecord
from network_links import NetworkLink
import pytest
import os

NEEDED_FILES = ['NWK', 'LOC']


class TestFiles:
    def test_files(self):
        for f_name in NEEDED_FILES:
            assert os.path.isfile(f_name)


class TestApplication:

    Main.import_location()
    Main.import_network_links()

    def test_simple(self, capfd):

        path = Pathfinder("CREWE", "DRBY")
        path.search()

        out = capfd.readouterr().out
        assert out == 'CREWE\nCREWSJN\nBTHLYJN\nALSAGER\nKIDSGRV\nSTOKEOT\nSTOKOTJ\nLNTN\nCAVRSWL\nUTOXSB\nTUTBURY\nNSJDRBY\nSTSNJN\nDRBYLNW\nDRBY\n'

    def test_avoid(self, capfd):

        path = Pathfinder("CREWE", "DRBY", avoid=['ALSAGER'])
        path.search()

        out = capfd.readouterr().out
        assert 'CREWE' in out
        assert 'DRBY' in out
        assert not 'ALSAGER' in out

    def test_via(self, capfd):

        path = Pathfinder("CREWE", "DRBY", via=['STAFFRD'])
        path.search()
        out = capfd.readouterr().out
        assert 'CREWE' in out
        assert 'DRBY' in out
        assert not 'ALSAGER' in out
