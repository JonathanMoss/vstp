"""Class and methods to create a Pathfinder and Node instance
"""

# pylint: disable=R0914
# pylint: disable=R0903
# pylint: disable=R0902
# pylint: disable=R0912
# pylint: disable=R0915

import sys
from network_links import NetworkLink
from location_record import LocationRecord


class Node:
    """Pathfinder Node"""

    def __init__(self, tiploc, parent=None):
        """Initialisation"""

        self.tiploc = tiploc
        self.parent = parent

        self.path_cost = 999999
        self.distance_to_go = 0
        self.heuristic = 999999

        self.m_dist = 0

    def __eq__(self, other):
        """Permits an == calculation to be made"""

        return self.tiploc == other.tiploc

    def __lt__(self, other):
        """Permits an < calculation to be made"""
        return True


class Pathfinder:
    """Class for finding the path between a TIPLOC pair"""

    def __init__(self, start_tiploc: str, end_tiploc: str, via=None):
        """Initialisation"""

        print(f'Calculating route from: {start_tiploc} to: {end_tiploc}...')
        print()

        self.via = via
        self.visited = []

        # Create start and end nodes
        self.start = start_tiploc
        self.visited.append(start_tiploc)

        self.start_coord = LocationRecord.return_instance(
            self.start).wgs_coordinates

        self.end = end_tiploc
        self.end_coord = LocationRecord.return_instance(
            self.end).wgs_coordinates

        start_node = Node(
            self.start
        )

        start_node.distance_to_go = LocationRecord.distance(
            self.start_coord,
            self.end_coord
        )

        start_node.heuristic = start_node.distance_to_go

        end_node = Node(
            self.end
        )

        self.openset = []
        self.closedset = []

        # Add the start node to the priority queue
        self.openset.append(start_node)

        while self.openset:  # Loop until find the end

            # Get the current node
            cur_node = min(self.openset, key=lambda o: o.heuristic)

            # Found the end goal
            if cur_node == end_node:
                path = []
                while cur_node.parent:
                    path.append(cur_node)
                    cur_node = cur_node.parent
                path.append(cur_node)

                for result in path[::-1]:
                    print(result.tiploc)
                sys.exit()

            # Remove the item from the open set
            self.openset.remove(cur_node)

            # Add it to the closedset
            self.closedset.append(cur_node)

            cur_path_cost = cur_node.path_cost
            cur_distance_to_go = cur_node.distance_to_go
            cur_tpl = cur_node.tiploc

            if cur_node.parent:
                cur_reversable = NetworkLink.reversable_data(
                    cur_node.parent.tiploc, cur_tpl)
            else:
                cur_reversable = {}

            # Create child nodes
            for tpl in NetworkLink.get_neighbours(cur_tpl):

                rev = NetworkLink.reversable_data(cur_tpl, tpl)
                if not cur_reversable.get(
                        'final_direction',
                        rev['inital_direction']
                ) == rev['inital_direction']:
                    if rev['reversable'] == "N":
                        continue

                if tpl in self.visited:
                    continue

                self.visited.append(tpl)

                new_node = Node(tpl, parent=cur_node)

                # Path Cost (Distance to parent)
                path_cost = NetworkLink.distance(
                    new_node.parent.tiploc,
                    tpl
                )

                new_node.m_dist = path_cost

                if int(path_cost) == 0 or int(path_cost) == 999999:
                    path_cost = cur_path_cost

                tpl_coord = LocationRecord.return_instance(tpl).wgs_coordinates

                # Distance to go (Distance ATCF to end TIPLOC)
                distance_to_go = LocationRecord.distance(
                    tpl_coord,
                    self.end_coord
                )

                if not distance_to_go:
                    distance_to_go = cur_distance_to_go

                if new_node in self.closedset:
                    continue

                if new_node in self.openset:
                    new_heuristic = cur_node.heuristic + path_cost
                    if new_node.heuristic > new_heuristic:
                        new_node.heuristic = new_heuristic
                        new_node.parent = cur_node
                else:
                    new_node.path_cost = cur_path_cost + path_cost
                    new_node.distance_to_go = distance_to_go
                    new_node.parent = cur_node
                    self.openset.append(new_node)
