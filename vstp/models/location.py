"""Representation of a BPLAN LOC record"""

# pylint: disable=E1101

import os
from typing import Optional, Union

import pydantic
from bng_latlon import OSGB36toWGS84 as conv
from haversine import Unit, haversine
from sqlmodel import Field, Session, SQLModel, create_engine

DB_CON_STRING = os.getenv("DB_CON_STRING", 'sqlite:///vstp.db')
LOC_FILE = os.getenv("LOC_FILE", 'LOC')
EAST_L = 135263
EAST_U = 658013
NORTH_L = 10866
NORTH_U = 969710

class Location(SQLModel, table=True):
    """Representaion of a LOC record from BPLAN"""

    id: Optional[int] = Field(default=None, primary_key=True)

    tiploc: str = pydantic.Field(
        title='Location TIPLOC code',
        min_length=3,
        max_length=7,
        regex="^[0-9A-Z]{3,7}$"
    )

    name: str = pydantic.Field(
        title='Location Name',
        max_length=32
    )

    easting: Union[str, None] = pydantic.Field(
        title='OS Easting',
        max_length=6,
        min_length=5,
        regex="^[0-9]{5,6}"
    )

    northing: Union[str, None] = pydantic.Field(
        title='OS Northing',
        max_length=6,
        min_length=5,
        regex="^[0-9]{5,6}"
    )

    tp_type: str = pydantic.Field(
        title='Timing point type (TMO)',
        min_length=1,
        max_length=1,
        regex="^[TMO]{1}$"
    )

    zone: str = pydantic.Field(
        title='Network Rail Zone',
        min_length=1,
        max_length=1,
        regex="^[0-9]{1}$"
    )

    stanox: Union[str, None] = pydantic.Field(
        title='STANOX code',
    )

    off_network: str = pydantic.Field(
        title='Off network indicator',
        min_length=1,
        max_length=1,
        regex="^[YN]$"
    )

    lpb: Union[str, None] = pydantic.Field(
        title='Line/Path/Both/Neither(None)',
        min_length=1,
        max_length=1,
        regex="^[LPB]{1}$"
    )

    @pydantic.validator('*', pre=True)
    @classmethod
    def strip_strings(cls, value: str) -> Union[str, None]:
        """Strip string"""
        if not value:
            return value
        stripped = value.strip()
        if not stripped:
            return None
        return stripped

    @pydantic.validator('stanox', pre=True)
    @classmethod
    def validate_stanox(cls, value: str) -> Union[str, None]:
        """Validate stanox"""

        stripped = value.strip()
        if len(stripped) < 5:
            return None
        if not stripped.isdigit():
            return None
        return stripped

    @pydantic.validator('easting', 'northing', pre=True)
    @classmethod
    def validate_os_coord(cls, value: str) -> Union[str, None]:
        """Validate the OS Coordinates (Easting/Northing)"""
        if not value:
            return None
        stripped = value.strip()
        if not stripped:
            return None

        if len(stripped) < 5:
            return None

        return stripped

    @classmethod
    @pydantic.validate_arguments
    def bplan_factory(cls, bplan_line: str) -> Union[object, None]:
        """Return a TimingLoad object from a BPLAN TLD line entry"""
        if not bplan_line.strip():
            return None
        values = bplan_line.split('\t')
        if not len(values) == 13:
            return None

        val_dict= {
            'tiploc': values[2],
            'name': values[3],
            'easting': values[6],
            'northing': values[7],
            'tp_type': values[8],
            'zone': values[9],
            'stanox': values[10],
            'off_network': values[11],
            'lpb': values[12]
        }

        obj =  cls(**val_dict)
        # Need to do this because we are mixing pydantic with SQLModel!
        # https://github.com/tiangolo/sqlmodel/issues/52

        obj.validate(val_dict)

        return obj

    @property
    def bng_coordinates(self) -> tuple:
        """Return Easting/Northing as a tuple"""

        return (self.easting, self.northing)

    @property
    def wgs_coordinates(self) -> Union[tuple, None]:
        """Return WGS [lat, lon] coordinates as a tuple"""

        if not all(self.bng_coordinates):
            return None

        return conv(int(self.easting), int(self.northing))

    @property
    def are_coords_valid(self) -> bool:
        """Return True if the easting/northing is valid"""

        if not all([self.easting, self.northing]):
            return False

        if int(self.easting) not in range(EAST_L, EAST_U):
            return False

        if int(self.northing) not in range(NORTH_L, NORTH_U):
            return False

        return True

    @classmethod
    @pydantic.validate_arguments
    def distance(cls, wgs_1: tuple, wgs_2: tuple, miles=True) -> Union[float, int]:
        """Provide 2 valid lat/lon [WGS] coordinate pairs, get a float/int back
        that is the distance, as the crow flies, twixt the two"""

        unit = Unit.MILES

        if not miles:
            unit = Unit.METERS
        try:
            return haversine(wgs_1, wgs_2, unit=unit)
        except Exception:  # pylint: disable=W0703
            return None

def main():
    """Entry point if running module"""
    engine = create_engine(DB_CON_STRING, echo=False)
    session = Session(engine)
    SQLModel.metadata.create_all(engine)

    with open(LOC_FILE, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            session.add(Location.bplan_factory(line))

    session.commit()

if __name__ == "__main__":
    main()
