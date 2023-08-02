"""A representation of a TLK record from BPLAN"""

# pylint: disable=E1101

from datetime import datetime
import os
from typing import Union, Optional
from sqlmodel import SQLModel, Field, Session, create_engine
import pydantic

DB_CON_STRING = os.getenv("DB_CON_STRING", 'sqlite:///vstp.db')
TLK_FILE = os.getenv("TLK_FILE", 'TLK')

class TimingLink(SQLModel, table=True):
    """Representation of a TLK record from BPLAN"""

    id: Optional[int] = Field(default=None, primary_key=True)

    origin: str = pydantic.Field(
        title='Origin TIPLOC',
        max_length=7,
        min_length=3,
        regex="^[A-Z0-9]{3,7}$"
    )

    destination: str = pydantic.Field(
        title='Destination TIPLOC',
        max_length=7,
        min_length=3,
        regex="^[A-Z0-9]{3,7}$"
    )

    line_code: Union[str, None] = pydantic.Field(
        title='Running line code',
        max_length=3,
        min_length=1,
        regex="^[A-Z0-9]{1,3}$",
    )

    traction_type: str = pydantic.Field(
        title='Traction type',
        min_length=2,
        max_length=6,
        regex="^[0-9A-Za-z-+/]{2,6}$"
    )

    trailing_load: Union[str, None] = pydantic.Field(
        title='Training load in tonnes',
        min_length=1,
        max_length=5,
        regex="^[0-9]{1,5}$"
    )

    speed: Union[str, None] = pydantic.Field(
        title='Maximum speed',
        min_length=1,
        max_length=3,
        regex="^[0-9]{1,3}$"
    )

    route_guage: Union[str, None] = pydantic.Field(
        title='Route availability code',
        min_length=1,
        max_length=3,
        regex="^[0-9A-Z]{1,3}$"
    )

    entry_speed: str = pydantic.Field(
        title='Entering the section - starting or passing',
        min_length=1,
        max_length=2,
        regex="^[0-1-]{1,2}$"
    )

    exit_speed: str = pydantic.Field(
        title='Exiting the section - stopping or passing',
        min_length=1,
        max_length=2,
        regex="^[0-1-]{1,2}$"
    )

    srt: str = pydantic.Field(
        title='Sectional running times mmm\'ss',
        min_length=3,
        max_length=7,
        regex="^[0-9'+]{3,7}$"
    )

    @property
    def running_time(self) -> int:
        """Return the SRT in seconds"""
        raw = datetime.strptime(
            self.srt,
            "+%M'%S"
        )

        raw_time = raw.time()
        return (raw_time.minute * 60) + raw_time.second

    @pydantic.validator('line_code', pre=True)
    @classmethod
    def to_upper(cls, value: str) -> Union[str, None]:
        """Convert to upper case"""
        if value:
            return value.upper()
        return value

    @pydantic.validator('*', pre=True)
    @classmethod
    def strip_strings(cls, value: str) -> Union[str, None]:
        """Strip string"""
        stripped = value.strip()
        if not stripped:
            return None
        return stripped

    @property
    def as_bplan(self) -> str:
        """Return the record, as specified in the BPLAN schema"""

        def to_string(value: object, pad=0) -> str:
            """Return string if None"""
            if not value:
                return "".ljust(pad, ' ')

            if value.isdigit():
                if not int(value):
                    return ""

            return value

        retval = f"TLK\tA\t{self.origin}\t{self.destination}\t{to_string(self.line_code)}\t"
        retval += f"{self.traction_type}\t{to_string(self.trailing_load)}\t{self.speed}\t"
        retval += f"{to_string(self.route_guage)}\t{self.entry_speed}\t{self.exit_speed}\t"
        retval += f"01-01-1970 00:00:00\t{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\t"
        retval += f"{self.srt}\t\n"

        return retval

    @classmethod
    @pydantic.validate_arguments
    def bplan_factory(cls, bplan_line: str) -> Union[object, None]:
        """Return a TimingLink object from a BPLAN TLK line entry"""
        if not bplan_line.strip():
            return None
        values = bplan_line.split('\t')
        if not len(values) == 15:
            return None

        val_dict = {
            'origin': values[2],
            'destination': values[3],
            'line_code': values[4],
            'traction_type': values[5],
            'trailing_load': values[6],
            'speed': values[7],
            'route_guage': values[8],
            'entry_speed': values[9],
            'exit_speed': values[10],
            'srt': values[13]  
        }

        obj =  cls(**val_dict)

        # Need to do this because we are mixing pydantic with SQLModel!
        # https://github.com/tiangolo/sqlmodel/issues/52
        obj.validate(val_dict)

        return obj

def main():
    """Entry point if running module"""
    engine = create_engine(DB_CON_STRING, echo=False)
    session = Session(engine)
    SQLModel.metadata.create_all(engine)

    with open(TLK_FILE, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            session.add(TimingLink.bplan_factory(line))

    session.commit()

if __name__ == "__main__":
    main()
