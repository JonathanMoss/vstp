"""Representation of NAPTAN train station coordinates"""

# pylint: disable=E0401

import os

import location as LOC
import pydantic
from bng_latlon import OSGB36toWGS84 as conv
from sqlmodel import Session, SQLModel, create_engine, select

DB_CON_STRING = os.getenv("DB_CON_STRING", 'sqlite:///vstp.db')
NAPTAN_9100 = os.getenv("NAPTAN_9100", '9100.csv')

class NAPTANCoordinates(SQLModel):
    """Representation of NAPTAN train station coordinates"""

    tiploc: str = pydantic.Field(
        title='Location TIPLOC code',
        min_length=3,
        max_length=7,
        regex="^[0-9A-Z]{3,7}$"
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
        """Return a NAPTANCoordinates object"""

        values = csv_line.split(',')

        val_dict = {
            'tiploc': values[0],
            'easting': values[1],
            'northing': values[2]
        }

        return cls(**val_dict)

def parse_naptan_file() -> list:
    """Parse the NAPTAN file, return a list of objects"""

    with open(NAPTAN_9100, 'r', encoding='utf-8') as csv:
        return [NAPTANCoordinates.csv_factory(line) for line in csv.readlines()]

def match_location(tiploc: str, session: Session) -> LOC.Location:
    """Return a matching location object, based on TIPLOC"""

    stmt = select(
        LOC.Location
    ).where(
        LOC.Location.tiploc == tiploc
    )

    return session.execute(stmt).fetchone()

def main():
    """Parse the NAPTAN file and update the database"""

    engine = create_engine(DB_CON_STRING, echo=False)
    with Session(engine) as session:
        for coord in parse_naptan_file():
            match = match_location(coord.tiploc, session)
            if not match:
                continue

            updated = []
            if not match[0].easting == coord.easting:
                updated.append(
                    f'Easting: {match[0].easting} -> {coord.easting}'
                )
                match[0].easting = coord.easting

            if not match[0].northing == coord.northing:
                updated.append(
                    f'Northing: {match[0].northing} -> {coord.northing}'
                )
                match[0].northing = coord.northing

            if not updated:
                print(f'TIPLOC: {coord.tiploc} - no amends!')
                continue

            print(f'TIPLOC: {coord.tiploc}: {updated}')

        session.commit()

if __name__ == '__main__':
    main()
