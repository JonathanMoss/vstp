"""A prepresentation of a NWK record from BPLAN"""

# pylint: disable=R0902

import json
import functools


class NetworkLink:
    """A prepresentation of a NWK record from BPLAN"""

    _instances = {}

    def __init__(self, *args):
        """Initialisation"""

        self.origin_location = args[2]
        self.destination_location = args[3]
        self.running_line_code = str(args[4]).strip()
        self.running_line_description = str(args[5]).strip()
        self.start_date = args[6]
        self.end_date = args[7]
        self.initial_direction = args[8]
        self.final_direction = args[9]
        self.distance = args[10]
        self.doo_p = args[11]
        self.doo_np = args[12]
        self.retb = args[13]
        self.zone = args[14]
        self.reversable = args[15]
        self.power = args[16]
        self.route_a = args[17]
        self.max_len = str(args[18]).strip('\n').strip()

    @classmethod
    @functools.lru_cache()
    def return_instance(cls, tiploc: str):
        """Return an instance matching the tiploc passed"""

        return cls._instances.get(tiploc, None)

    @property
    def as_dict(self) -> dict:
        """Return a dictionary representation of the object"""

        return {

            'origin_location': self.origin_location,
            'destination_location': self.destination_location,
            'running_line_code': self.running_line_code,
            'running_line_description': self.running_line_description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'initial_direction': self.initial_direction,
            'final_direction': self.final_direction,
            'distance': self.distance,
            'doo_p': self.doo_p,
            'doo_np': self.doo_np,
            'retb': self.retb,
            'zone': self.zone,
            'reversable': self.reversable,
            'power': self.power,
            'ra': self.route_a,
            'max_len': self.max_len

        }

    def __repr__(self) -> str:
        """Return a string representation of the object"""

        return json.dumps(
            self.as_dict,
            indent=4
        )

    def append_to_instance(self):
        """Append to the class instances"""

        if self.origin_location not in self._instances:
            self._instances.update({
                self.origin_location: {
                    self.destination_location: [
                        self
                    ]
                }
            })

        elif self.destination_location not in self._instances[self.origin_location]:
            self._instances[self.origin_location].update({
                self.destination_location: [
                    self
                ]
            })

        else:
            self._instances[self.origin_location][self.destination_location].append(self)

    @classmethod
    @functools.lru_cache()
    def distance(cls, tiploc_a: str, tiploc_b: str) -> int:
        """Calculate the distance between tiploc A and tiploc B"""

        if tiploc_a not in cls._instances:
            return None

        if tiploc_b not in cls._instances[tiploc_a]:
            return None

        _min = 999999
        for entry in cls._instances[tiploc_a][tiploc_b]:
            if str(entry.distance).strip() == '':
                continue
            if int(entry.distance) != 0 and int(entry.distance) < _min:
                _min = int(entry.distance)

        return min

    @classmethod
    @functools.lru_cache()
    def reversable_data(cls, tiploc_a, tiploc_b) -> dict:
        """Pass a TIPLOC pair, get the directions and reversable data"""

        if tiploc_a not in cls._instances:
            return None

        if tiploc_b not in cls._instances[tiploc_a]:
            return None

        initial_dir = "U"
        final_dir = "U"
        reversable = "N"

        for entry in cls._instances[tiploc_a][tiploc_b]:
            initial_dir = entry.initial_direction
            final_dir = entry.final_direction
            reversable = entry.reversable

        return {
            'inital_direction': initial_dir,
            'final_direction': final_dir,
            'reversable': reversable
        }

    @classmethod
    @functools.lru_cache()
    def get_neighbours(cls, tiploc: str) -> list:
        """Pass a tiploc, return a list of all reachable TIPLOCS"""

        if not tiploc in cls._instances:
            return []

        return cls._instances[tiploc].keys()
