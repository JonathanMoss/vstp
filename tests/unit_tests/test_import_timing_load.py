"""Unit tests for import_timing_loads
"""

import os
import sys
sys.path.insert(0, './vstp')  # nopep8
import pytest
import import_timing_load as TLD


class TestEnvVars:
    def test_env(self):
        assert TLD.ENGINE.__class__.__name__ == 'Engine'
        assert TLD.SESSION.__class__.__name__ == 'Session'
        assert hasattr(TLD, 'TimingLoad')
        assert hasattr(TLD, 'Base')


class TestImport:
    def test_strip_value(self):
        assert TLD.strip_value('') == None
        assert TLD.strip_value(' foo ') == 'foo'

    def test_import_timing_loads(self, monkeypatch):
        if os.path.exists('tld.db'):
            os.remove('tld.db')

        with monkeypatch.context() as monkey:
            monkey.setattr(
                'import_timing_load.import_from_file',
                lambda filename: [
                    ['foo' for _ in range(10)]
                ]
            )

            TLD.import_timing_loads()

        assert os.path.exists('tld.db')
        os.remove('tld.db')
