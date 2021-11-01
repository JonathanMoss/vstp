"""Integration tests for the application"""

import pytest
import os
import main as Main
from err import MissingPartFile, BadTiplocError
from pathfinder import Pathfinder
from location_record import LocationRecord
from network_links import NetworkLink

NEEDED_FILES = ['NWK', 'LOC']


class TestFiles:
    def test_files(self):
        for f_name in NEEDED_FILES:
            assert os.path.isfile(f_name)


class TestApplication:

    Main.import_location()
    Main.import_network_links()

    def test_file_missing(self):
        with pytest.raises(MissingPartFile) as err:
            Main.import_from_file('missing.part.file')

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

    def test_bad_tiploc(self):

        with pytest.raises(BadTiplocError) as err:
            path = Pathfinder("CREWE", "FOO")
            path.search()

            path = Pathfinder("CREWE", "DRBY", via=['FOO'])
            path.search()

            path = Pathfinder("CREWE", "DRBY", avoid=['FOO'])
            path.search()
