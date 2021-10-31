"""Unit tests for pathfinder"""

import pytest
from pathfinder import Node, Pathfinder
from err import BadAvoidList, BadViaList, BadTiplocError


class DummyRecord:
    def __init__(self):
        self.wgs_coordinates = (53.08566483961731, -2.2448107258158285)


class TestNode:
    def test_init(self):
        node = Node('foo')
        assert node.__class__.__name__ == 'Node'
        assert not node.parent

    def test_eq(self):
        node = Node('foo')
        node_b = Node('foo')
        assert node == node_b
        node_b = Node('bar')
        assert not node == node_b

    def test_lt(self):
        node = Node('foo')
        assert node < 0


class TestPathfinder:
    def test_init(self, monkeypatch):

        with pytest.raises(BadTiplocError) as err:
            Pathfinder('FOO', 'BAR')

        with monkeypatch.context() as monkey:

            monkey.setattr(
                'pathfinder.LocationRecord.return_instance',
                lambda *args, **kwargs: DummyRecord()
            )
            monkey.setattr(
                'pathfinder.Pathfinder.validate_tiploc',
                lambda tiploc: True
            )
            with pytest.raises(BadViaList):
                Pathfinder('FOO', 'BAR', via='BAZ')
            with pytest.raises(BadAvoidList):
                Pathfinder('FOO', 'BAR', avoid='BAZ')

            result = Pathfinder(
                'FOO',
                'BAR',
                via=['BAZ'],
                avoid=['BIZ']
            )

            assert len(result.routing_leg_nodes) == 3

    def test_validate_tiploc(self):
        with pytest.raises(BadTiplocError):
            Pathfinder.validate_tiploc('BADTPL')

    @pytest.mark.xfail
    def test_search(self):
        # FOR INTEGRATION TESTING
        assert False

    @pytest.mark.xfail
    def test_process_leg(self):
        # FOR INTEGRATION TESTING
        assert False
