"""Location Records are a representation of a LOC record from the BPLAN"""

# pylint: disable=R0902
# pylint: disable=R1716
# pylint: disable=E0611

import json

from fuzzyfinder import fuzzyfinder

from bng_latlon import OSGB36toWGS84 as conv
from haversine import haversine, Unit

EAST_L = 135263
EAST_U = 658013
NORTH_L = 10866
NORTH_U = 969710


class LocationRecord:
    """Representation of the LOC record"""

    _instances = {}

    def __init__(self, *args):
        """Initialisation"""

        self.location_code = args[2]
        self.location_name = args[3]
        self.start_date = args[4]
        self.end_date = args[5]
        self.os_easting = int(args[6])
        self.os_northing = int(args[7])
        self.timing_point_type = args[8]
        self.zone = args[9]
        self.stanox_code = args[10]
        self.off_network_indicator = args[11]
        self.force_lpb = str(args[12]).strip('\n').strip()
        self._instances[self.location_code] = self

    @property
    def as_dict(self) -> dict:
        """Return the object represented as a dictionary"""

        return {
            'location_code': self.location_code,
            'location_name': self.location_name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'easting/northing': self.bng_coordinates,
            'lat/lon': self.wgs_coordinates,
            'timing_point_type': self.timing_point_type,
            'zone': self.zone,
            'stanox': self.stanox_code,
            'off_network_indicator': self.off_network_indicator,
            'force_lpb': self.force_lpb
        }

    def __repr__(self) -> str:
        """Return a string representation of the object"""

        return json.dumps(self.as_dict)

    @staticmethod
    def distance(wgs_1: tuple, wgs_2: tuple) -> float:
        """Provide 2 valid lat/lon [WGS] coordinate pairs, get a float back
        that is the distance, as the crow flies, twixt the two"""

        try:
            return haversine(wgs_1, wgs_2, unit=Unit.MILES)
        except Exception:  # pylint: disable=W0703
            return None

    @classmethod
    def match_locations(cls, search: str) -> list:
        """Returns a list of matching locations"""
        ret_val = []
        for _, obj in cls._instances.items():
            match = fuzzyfinder(search, [obj.location_code, obj.location_name])
            if list(match):
                ret_val.append(f'{obj.location_code}:{obj.location_name}')
        return ret_val

    @classmethod
    def return_instance(cls, tiploc: str):
        """Return an instance matching the tiploc passed"""

        return cls._instances.get(tiploc, None)

    @staticmethod
    def valid_coord(os_coord: int, coord_type: str) -> bool:
        """Return True if it is a valid easting/northing, otherwise False"""

        if coord_type == "northing":
            if os_coord >= NORTH_L and os_coord <= NORTH_U:
                return True
        else:
            if os_coord >= EAST_L and os_coord <= EAST_U:
                return True

        return False

    @property
    def bng_coordinates(self) -> tuple:
        """Return Easting/Northing as a tuple (or None if invalid)"""

        if not self.valid_coord(self.os_easting, 'easting'):
            return None

        if not self.valid_coord(self.os_northing, 'northing'):
            return None

        return (self.os_easting, self.os_northing)

    @property
    def wgs_coordinates(self) -> tuple:
        """Return WGS [lat, lon] coordinates as a tuple (or None if invalid)"""

        bng = self.bng_coordinates
        if not bng:
            return None

        try:
            return conv(self.os_easting, self.os_northing)
        except Exception:  # pylint: disable=W0703
            return None
