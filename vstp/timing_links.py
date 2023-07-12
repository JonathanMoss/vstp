"""A representation of a TLK record from BPLAN"""

# pylint: disable=E1101

from typing import Union, Optional
from sqlmodel import SQLModel, Field, Session, create_engine
import pydantic

class TimingLink(SQLModel, table=True):
    """Representation of a TLK record from BPLAN"""

    id: Optional[int] = Field(default=None, primary_key=True)
    
    origin: str = pydantic.Field(
        title='Origin TIPLOC',
        max_len=7,
        min_len=3,
        regex='[A-Z0-9]{3,7}'
    )

    destination: str = pydantic.Field(
        title='Destination TIPLOC',
        max_len=7,
        min_len=3,
        regex='[A-Z0-9]{3,7}'
    )

    line_code: Union[str, None] = pydantic.Field(
        title='Running line code',
        max_len=3,
        regex='[A-Z0-9]{0,3}'
    )

    traction_type: str = pydantic.Field(
        title='Traction type',
        min_len=2,
        max_len=6,
        regex='[0-9A-Za-z-]{2,6}'
    )

    trailing_load: Union[str, None] = pydantic.Field(
        title='Training load in tonnes',
        min_len=1,
        max_len=5,
        regex='[0-9]{1,5}'
    )

    speed: Union[str, None] = pydantic.Field(
        title='Maximum speed',
        min_len=1,
        max_len=3,
        regex='[0-9]{1,3}'
    )

    route_guage: Union[str, None] = pydantic.Field(
        title='Route availability code',
        min_len=1,
        max_len=3,
        regex='[0-9A-Z]{1,3}'
    )

    entry_speed: str = pydantic.Field(
        title='Entering the section - starting or passing',
        min_len=1,
        max_len=2,
        regex='[0-1-]{1,2}'
    )

    exit_speed: str = pydantic.Field(
        title='Exiting the section - stopping or passing',
        min_len=1,
        max_len=2,
        regex='[0-1-]{1,2}'
    )

    srt: str = pydantic.Field(
        title='Sectional running times mmm\'ss',
        min_len=3,
        max_len=7,
        regex="[0-9'+]{3,6}"
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
        """Return a TimingLink object from a BPLAN TLK line entry"""
        if not bplan_line.strip():
            return None
        values = bplan_line.split('\t')
        if not len(values) == 15:
            return None
        return cls(
            origin=values[2],
            destination=values[3],
            line_code=values[4],
            traction_type=values[5],
            trailing_load=values[6],
            speed=values[7],
            route_a=values[8],
            entry_speed=values[9],
            exit_speed=values[10],
            srt=values[13]
        )
def main():
    engine = create_engine("sqlite:///tlk.db", echo=True)
    session = Session(engine)
    SQLModel.metadata.create_all(engine)
    
    with open('TLK', 'r') as file:
        for line in file.readlines()[:5]:
            session.add(TimingLink.bplan_factory(line))
            
    session.commit()
    
if __name__ == "__main__":
    main()
