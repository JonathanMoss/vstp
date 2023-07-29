"""Representation of the FOI TIPLOC coordinate request data"""

# pylint: disable=E0401

import os

import location as LOC
import pydantic
from bng_latlon import OSGB36toWGS84 as conv
from sqlmodel import Session, SQLModel, create_engine, select

DB_CON_STRING = os.getenv("DB_CON_STRING", 'sqlite:///vstp.db')
FOI_FILE = os.getenv("FOI_FILE", 'FOI_easting_northing.csv')

class FOICoordinates(SQLModel):
    """Representation of the FOI TIPLOC coordinate request data"""

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

    easting: str = pydantic.Field(
        title='OS Easting',
        max_length=6,
        min_length=5,
        regex="^[0-9]{5,6}"
    )

    northing: str = pydantic.Field(
        title='OS Northing',
        max_length=6,
        min_length=5,
        regex="^[0-9]{5,6}"
    )

    @pydantic.validator('*', pre=True)
    @classmethod
    def strip_strings(cls, value: str) -> str:
        """Strip string"""

        stripped = value.strip()
        if not stripped:
            return None
        return stripped

    @property
    def bng_coordinates(self) -> tuple:
        """Return Easting/Northing as a tuple"""

        return (self.easting, self.northing)

    @property
    def wgs_coordinates(self) -> tuple:
        """Return WGS [lat, lon] coordinates as a tuple"""

        return conv(int(self.easting), int(self.northing))

    @classmethod
    @pydantic.validate_arguments
    def csv_factory(cls, csv_line: str) -> object:
        """Return a FOICoordinates object"""

        values = csv_line.split(',')

        val_dict = {
            'tiploc': values[0],
            'name': values[1],
            'easting': values[2],
            'northing': values[3]
        }

        return cls(**val_dict)

def parse_foi_file() -> list:
    """Parse the FOI file, return a list of objects"""

    with open(FOI_FILE, 'r', encoding='utf-8') as csv:
        return [FOICoordinates.csv_factory(line) for line in csv.readlines()]

def match_location(tiploc: str, session: Session) -> LOC.Location:
    """Return a matching location object, based on TIPLOC"""

    stmt = select(
        LOC.Location
    ).where(
        LOC.Location.tiploc == tiploc
    )

    return session.execute(stmt).fetchone()

def main():
    """Parse the FOI file and update the database"""

    engine = create_engine(DB_CON_STRING, echo=False)
    with Session(engine) as session:
        for coord in parse_foi_file():
            match = match_location(coord.tiploc, session)
            if not match:
                new = LOC.Location(
                    tiploc=coord.tiploc,
                    easting=coord.easting,
                    northing=coord.northing,
                    name=coord.name,
                    tp_type='O',
                    zone='0',
                    off_network='N'
                )
                session.add(new)
                continue
            
            if match[0].easting == '999999':
                match[0].easting = None
                
            if match[0].northing == '999999':
                match[0].northing = None
                
            if not match[0].easting:
                match[0].easting = coord.easting
                
            if not match[0].northing:
                match[0].northing = coord.northing
                
            # if not match[0].easting == coord.easting:
            #     match[0].easting = coord.easting

            # if not match[0].northing == coord.northing:
            #     match[0].northing = coord.northing

        session.commit()

if __name__ == '__main__':
    main()
