"""Representation of a BPLAN NWK record"""

from datetime import datetime
import os
from typing import Union, Optional
from sqlmodel import SQLModel, Field, Session, create_engine
import pydantic

DB_CON_STRING = os.getenv("DB_CON_STRING", 'sqlite:///vstp.db')
NWK_FILE = os.getenv("NWK_FILE", 'NWK')

class NetworkLink(SQLModel, table=True):
    """Representation of a BPLAN NWK record"""

    id: Optional[int] = Field(default=None, primary_key=True)

    origin: str = pydantic.Field(
        title='Origin location',
        min_length=3,
        max_length=7,
        regex="^[0-9A-Z]{3,7}$"
    )

    destination: str = pydantic.Field(
        title='Destination location',
        min_length=3,
        max_length=7,
        regex="^[0-9A-Z]{3,7}$"
    )

    line: Union[str, None] = pydantic.Field(
        title='Running line code',
        min_length=1,
        max_length=3,
        regex="^[0-9A-Z]{1,3}$"
    )

    line_desc: Union[str, None] = pydantic.Field(
        title='Description for running line code',
        max_length=20
    )

    initial_dir: str = pydantic.Field(
        title='Initial direction',
        max_length=1,
        min_length=1,
        regex="^[UD]{1}"
    )

    final_dir: str = pydantic.Field(
        title='Final direction',
        max_length=1,
        min_length=1,
        regex="^[UD]{1}"
    )

    distance: Union[str, None] = pydantic.Field(
        title='Distance in metres',
        max_length=5,
        min_length=1,
        regex="^[0-9]{1,5}$"
    )

    doop: str = pydantic.Field(
        title='Driver only operation (passenger)',
        min_length=1,
        max_length=1,
        regex="^[YN]{1}$"
    )

    doof: str = pydantic.Field(
        title='Driver only operation (freight)',
        min_length=1,
        max_length=1,
        regex="^[YN]{1}$"
    )

    retb: str = pydantic.Field(
        title='RETB in operation',
        min_length=1,
        max_length=1,
        regex="^[YN]{1}$"
    )

    zone: Union[str, None] = pydantic.Field(
        title='NR Zone (ex-BR)',
        min_length=1,
        max_length=1,
        regex="^[0-9]{1}$"
    )

    reversable: str = pydantic.Field(
        title='Is line reversable',
        min_length=1,
        max_length=1,
        regex="^[BRN]{1}$"
    )

    power: Union[str, None] = pydantic.Field(
        title='Power supply type code',
        min_length=1,
        max_length=1,
        regex="^[A-Z]{1}$"
    )

    route_avail: str = pydantic.Field(
        title='Route availability number',
        min_length=1,
        max_length=2,
        regex="^[A-Z0-9]{1,2}$"
    )

    max_len: Union[str, None] = pydantic.Field(
        title='Maximum train length',
        min_length=1,
        max_length=5,
        regex="^[0-9]{1,5}$"
    )

    @pydantic.validator('line', pre=True)
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

        retval = f"NWK\tA\t{self.origin}\t{self.destination}\t{to_string(self.line)}\t"
        retval += f"{to_string(self.line_desc)}\t01-01-1970 00:00:00\t"
        retval += f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\t{self.initial_dir}\t"
        retval += f"{self.final_dir}\t{self.distance}\t{self.doop}\t"
        retval += f"{self.doof}\t{self.retb}\t{self.zone}\t{self.reversable}\t"
        retval += f"{to_string(self.power)}\t{self.route_avail}\t{to_string(self.max_len)}\n"

        return retval

    @classmethod
    @pydantic.validate_arguments
    def bplan_factory(cls, bplan_line: str) -> Union[object, None]:
        """Return a NetworkLink object from a BPLAN NWK line entry"""
        if not bplan_line.strip():
            return None
        values = bplan_line.split('\t')
        if not len(values) == 19:
            return None

        val_dict= {
            'origin': values[2],
            'destination': values[3],
            'line': values[4],
            'line_desc': values[5],
            'initial_dir': values[8],
            'final_dir': values[9],
            'distance': values[10],
            'doop': values[11],
            'doof': values[12],
            'retb': values[13],
            'zone': values[14],
            'reversable': values[15],
            'power': values[16],
            'route_avail': values[17],
            'max_len': values[18]
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

    with open(NWK_FILE, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            session.add(NetworkLink.bplan_factory(line))

    session.commit()

if __name__ == "__main__":
    main()
