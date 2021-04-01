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

        self.path_cost = 0
        self.distance_to_go = 0
        self.heuristic = 0

        self.m_dist = 0

    def __eq__(self, other):
        """Permits an == calculation to be made"""

        return self.tiploc == other.tiploc

    def __lt__(self, other):
        """Permits an < calculation to be made"""
        return True


class Pathfinder:
    """Class for finding the path between a TIPLOC pair"""

    def __init__(self, start_tiploc: str, end_tiploc: str, via=None, avoid=[]):
        """Initialisation"""

        self.via = via  # Tiplocs where the service MUST run via
        if self.via and not isinstance(self.via, list):
            print('VIA tiplocs not provided in required format')
            sys.exit(1)

        self.avoid = avoid  # Tiplocs where the service MUST avoid
        if self.avoid and not isinstance(self.avoid, list):
            print('AVOID tiplocs not provided in required format')
            sys.exit(1)

        self.legs = []
        self.routing_leg_nodes = []

        # Create Start Node
        self.routing_leg_nodes.append(Node(start_tiploc))

        # Create via Node(s)
        if isinstance(via, list):
            for tiploc in via:
                self.routing_leg_nodes.append(Node(tiploc))

        # Create End Node
        self.routing_leg_nodes.append(Node(end_tiploc))

        # Create routing legs
        for index, _ in enumerate(self.routing_leg_nodes):

            if index == len(self.legs):
                continue

            self.legs.append(
                [index - 1, index]
            )

        # Enrich legs with info needed to process
        for leg in self.legs:

            node_a_coord = LocationRecord.return_instance(
                self.routing_leg_nodes[leg[0]].tiploc).wgs_coordinates

            node_b_coord = LocationRecord.return_instance(
                self.routing_leg_nodes[leg[1]].tiploc).wgs_coordinates

            self.routing_leg_nodes[leg[0]].distance_to_go = LocationRecord.distance(
                node_a_coord,
                node_b_coord
            )

            self.routing_leg_nodes[leg[0]].heuristic = self.routing_leg_nodes[leg[0]].distance_to_go

            self.routing_leg_nodes[leg[1]].coords = node_b_coord

    def search(self):
        """Kick off the route finding"""

        for index, leg in enumerate(self.legs):

            tab = '\t' * (index)
            results = self.process_leg(
                self.routing_leg_nodes[leg[0]],
                self.routing_leg_nodes[leg[1]]
            )

            if not results:
                msg = f"\n{tab}MISSING LEG: {self.routing_leg_nodes[leg[0]].tiploc}"
                msg += f" to {self.routing_leg_nodes[leg[1]].tiploc}\n"
                print(msg)

            if results:
                for node in results:
                    print(f'{tab}{node.tiploc}')

    def process_leg(self, start_node, end_node) -> list:
        """Process the leg passed, return the results"""

        openset = []
        closedset = []

        # Add the start node to the priority queue
        openset.append(start_node)

        while openset:  # Loop until find the end

            # Get the current node
            cur_node = min(openset, key=lambda o: o.heuristic)

            # Found the end goal
            if cur_node == end_node:
                path = []
                while cur_node.parent:
                    path.append(cur_node)
                    cur_node = cur_node.parent
                path.append(cur_node)
                return path[::-1]

            # Remove the item from the open set
            openset.remove(cur_node)

            # Add it to the closedset
            closedset.append(cur_node)

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

                if tpl in self.avoid:
                    continue

                # This stops reversing movements where not authorised
                rev = NetworkLink.reversable_data(cur_tpl, tpl)
                if not cur_reversable.get(
                        'final_direction',
                        rev['inital_direction']
                ) == rev['inital_direction']:
                    if rev['reversable'] == "N":
                        continue

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
                    end_node.coords
                )

                if not distance_to_go:
                    distance_to_go = cur_distance_to_go

                if new_node in closedset:
                    continue

                if new_node in openset:
                    new_heuristic = cur_node.heuristic + path_cost
                    if new_node.heuristic > new_heuristic:
                        new_node.heuristic = new_heuristic
                        new_node.parent = cur_node
                else:
                    new_node.path_cost = cur_path_cost + path_cost
                    new_node.distance_to_go = distance_to_go
                    new_node.parent = cur_node
                    openset.append(new_node)
