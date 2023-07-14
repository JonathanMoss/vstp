"""A representation of a Timing Load TLD BPLAN record"""

import os
from typing import Union, Optional
from sqlmodel import SQLModel, Field, Session, create_engine
import pydantic

DB_CON_STRING = os.getenv("DB_CON_STRING", 'sqlite:///vstp.db')

class TimingLoad(SQLModel, table=True):
    """Representation of a TLD record from BPLAN"""

    id: Optional[int] = Field(default=None, primary_key=True)

    traction_type: str = pydantic.Field(
        title='Traction Type',
        max_len=6,
        min_len=1,
        regex='[0-9A-Z-]{1,6}'
    )

    trailing_load: Union[str, None] = pydantic.Field(
        title='Trailing Load (Tonnes)',
        max_len=5,
        min_len=1,
        regex='[0-9]{1,5}'
    )

    max_speed: Union[str, None] = pydantic.Field(
        title='Maximum Speed (MPH)',
        min_len=1,
        max_len=3,
        regex='[0-9]{1,3}'
    )

    ra_guage: Union[str, None] = pydantic.Field(
        title='Route Availability/Guage',
        min_len=1,
        max_len=3,
        regex='[A_Z]{1,3}'
    )

    description: str = pydantic.Field(
        title='Description',
        min_len=1,
        max_len=64
    )

    power_type: str = pydantic.Field(
        title='ITPS Power Type',
        min_len=1,
        max_len=3,
        regex='[A-Z]{1,3}'
    )

    load: Union[str, None] = pydantic.Field(
        title='ITPS Load',
        min_len=1,
        max_len=4,
        regex='[A-Z0-9]{1,3}'
    )

    limiting_speed: Union[str, None] = pydantic.Field(
        title='ITPS Limiting Speed',
        min_len=1,
        max_len=3,
        regex='[0-9]{1,3}'
    )

    @pydantic.validator('*', pre=True)
    @classmethod
    def strip_strings(cls, value: str) -> Union[str, None]:
        """Strip string"""
        stripped = value.strip()
        if not stripped:
            return None
        return stripped

    @classmethod
    @pydantic.validate_arguments
    def bplan_factory(cls, bplan_line: str) -> Union[object, None]:
        """Return a TimingLoad object from a BPLAN TLD line entry"""
        if not bplan_line.strip():
            return None
        values = bplan_line.split('\t')
        if not len(values) == 10:
            return None
        return cls(
            traction_type=values[2],
            trailing_load=values[3],
            speed=values[4],
            ra_guage=values[5],
            description=values[6],
            power_type=values[7],
            load=values[8],
            limiting_speed=values[9]
        )

def main():
    """Entry point if running module"""
    engine = create_engine(DB_CON_STRING, echo=True)
    session = Session(engine)
    SQLModel.metadata.create_all(engine)

    with open('TLD', 'r', encoding='utf-8') as file:
        for line in file.readlines():
            session.add(TimingLoad.bplan_factory(line))

    session.commit()

if __name__ == "__main__":
    main()