"""Representation of a SMART record"""

import json
import os
from typing import Optional, Union

import pydantic
from sqlmodel import Field, Session, SQLModel, create_engine

DB_CON_STRING = os.getenv("DB_CON_STRING", 'sqlite:///vstp.db')
SMART_FILE = os.getenv("SMART_FILE", 'SMARTExtract.json')

class Smart(SQLModel, table=True):
    """Representation of a SMART record"""

    id: Optional[int] = Field(default=None, primary_key=True)

    step_type: str = pydantic.Field(
        alias="STEPTYPE",
        regex="^[BFCDITE]{1}$"
    )

    from_berth: Union[str, None] = pydantic.Field(
        alias="FROMBERTH",
        regex="^[A-Z0-9]{4}$"
    )

    to_berth: Union[str, None] = pydantic.Field(
        alias="TOBERTH",
        regex="^[A-Z0-9]{4}$"
    )

    stanox: str = pydantic.Field(
        alias="STANOX",
        regex="^[0-9]{5}$"
    )

    event: Union[str, None] = pydantic.Field(
        alias="EVENT",
        regex="^[ABCD]{1}$"
    )

    platform: Union[str, None] = pydantic.Field(
        alias="PLATFORM",
        regex="^[0-9A-Z]{1,3}$"
    )

    to_line: Union[str, None] = pydantic.Field(
        alias="TOLINE",
        regex="^[0-9A-Z]{1,3}$"
    )

    berth_offset: str = pydantic.Field(
        alias="BERTHOFFSET",
        regex="^[+-0-9]{1,4}"
    )

    route: Union[str, None] = pydantic.Field(
        alias="ROUTE",
        regex="^[0-9A-Z]{1,3}$"
    )

    from_line: Union[str, None] = pydantic.Field(
        alias="FROMLINE",
        regex="^[0-9A-Z]{1,3}$"
    )

    td: str = pydantic.Field(
        alias="TD",
        regex="^[0-9A-Z]{2}$"
    )

    comment: Union[str, None] = pydantic.Field(
        alias="COMMENT"
    )

    stanme: Union[str, None] = pydantic.Field(
        title='STANME'
    )

    @pydantic.validator('*', pre=True)
    @classmethod
    def strip_strings(cls, value: str) -> Union[str, None]:
        """Strip string"""
        if not value:
            return None
        stripped = value.strip()
        if not stripped:
            return None
        return stripped

def main():
    """Entry point if running module"""
    engine = create_engine(DB_CON_STRING, echo=False)
    session = Session(engine)
    SQLModel.metadata.create_all(engine)

    with open(SMART_FILE, 'r', encoding='utf-8') as file:
        rep = json.loads(file.readline())
        for record in rep['BERTHDATA']:
            session.add(Smart(**record))

    session.commit()

if __name__ == "__main__":
    main()
