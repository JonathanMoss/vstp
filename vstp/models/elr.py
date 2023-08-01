"""Representation of an Engineers Line Reference"""

# pylint: disable=E1101

import os
import re
from typing import Optional, Union
import pydantic
from sqlmodel import Field, Session, SQLModel, create_engine

DB_CON_STRING = os.getenv("DB_CON_STRING", 'sqlite:///vstp.db')
ELR_MAPPING = os.getenv("ELR_MAPPING", './reference_data/elr_mapping.csv')
ELR_REFERENCE = os.getenv("ELR_REFERENCE", './reference_data/elr_references.csv')
PRIDE_LOR_CODES = os.getenv("PRIDE_LOR_CODES", './reference_data/pride_lor_codes.csv')

class EngineersLineRef(SQLModel, table=True):
    """Representation of an Engineers Line Reference Record"""

    id: Optional[int] = Field(default=None, primary_key=True)

    elr: str = pydantic.Field(
        title='ELR Code',
        min_length=3,
        max_length=4,
        regex="^[0-9A-Z_]{3,4}$"
    )

    name: str = pydantic.Field(
        title='Line name'
    )

    start_mileage: Union[float, None] = pydantic.Field(
        title='Start Mileage (Miles/Chains)'
    )

    end_mileage: Union[float, None] = pydantic.Field(
        title='End Mileage (Miles/Chains)'
    )

    datum: Union[str, None] = pydantic.Field(
        title='Reference location for mileage'
    )

    notes: Union[str, None] = pydantic.Field(
        title='Notes'
    )

    lor_reference: Union[str, None] = pydantic.Field(
        title='PRIDE/LOR code',
        min_length=4,
        max_length=7,
        regex="^[0-9A-Z]{4,7}$"
    )

    lor_name: Union[None, str] = pydantic.Field(
        title='PRIDE/LOR name'
    )

    ra_value: Union[None, int] = pydantic.Field(
        title='Route Availability (RA)'
    )

    @pydantic.validator('elr', 'name', 'datum', 'notes', pre=True)
    @classmethod
    def strip_strings(cls, value: str) -> Union[str, None]:
        """Strip string"""
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.lower() == 'nan':
            return None
        return stripped

    @staticmethod
    @pydantic.validate_arguments
    def extrapolate_mileage(mileages: str) -> list:
        """Extrapolate the start and end mileages from a string"""

        data = re.findall("[0-9.]{1,10}", mileages)
        if len(data) == 2:
            return data

        return [None, None]

    @classmethod
    @pydantic.validate_arguments
    def factory(cls, bplan_line: str) -> Union[object, None]:
        """Return a EngineerLineRef object from the CSV"""
        if not bplan_line.strip():
            return None
        values = bplan_line.split('\t')
        if not len(values) == 5:
            return None

        mileages = cls.extrapolate_mileage(values[2])

        val_dict = {
            'elr': values[0],
            'name': values[1],
            'start_mileage': mileages[0],
            'end_mileage': mileages[1],
            'datum': values[3],
            'notes': values[4]
        }

        obj =  cls(**val_dict)
        # Need to do this because we are mixing pydantic with SQLModel!
        # https://github.com/tiangolo/sqlmodel/issues/52

        obj.validate(val_dict)

        return obj

class LORPride(pydantic.BaseModel):
    """Representation of a LOR/PRIDE record"""

    code: str = pydantic.Field(
        title='LOR/PRIDE code',
        min_length=5,
        max_length=7,
        regex="^[0-9A-Z]{5,7}$"
    )

    name: str = pydantic.Field(
        title='LOR/PRIDE name'
    )

    ra_value: int = pydantic.Field(
        title='Route Availability (RA)',
    )

    @pydantic.validator('ra_value', pre=True)
    @classmethod
    def strip_ra(cls, value: str) -> int:
        """Extract the RA value"""
        value = re.match('[0-9]{1,2}', value)
        if value:
            return int(value[0])
        return 0

    @pydantic.validator('code', 'name', pre=True)
    @classmethod
    def strip_strings(cls, value: str) -> Union[str, None]:
        """Strip string"""
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.lower() == 'nan':
            return None
        return stripped

    @classmethod
    @pydantic.validate_arguments
    def factory(cls, line: str) -> Union[object, None]:
        """Instantiate a LORPride object from CSV line"""
        if not line.strip():
            return None
        values = line.split('\t')
        if not len(values) == 3:
            return None

        val_dict = {
            'code': values[0],
            'name': values[1],
            'ra_value': values[2]
        }

        return cls(**val_dict)

class ELRMapping(pydantic.BaseModel):
    """Representation of an ELR/LOR mapping record"""

    elr: str = pydantic.Field(
        title='ELR Code',
        min_length=3,
        max_length=4,
        regex="^[0-9A-Z]{3,4}$"
    )

    code: str = pydantic.Field(
        title='LOR/PRIDE code',
        min_length=5,
        max_length=7,
        regex="^[0-9A-Z]{5,7}$"
    )

    @pydantic.validator('code', pre=True)
    @classmethod
    def get_code(cls, value: str) -> Union[str, None]:
        """Extrapolates the LOR/PRIDE code"""
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.lower() == 'nan':
            return None
        match = re.match("[0-9A-Z]{5,7}", value)
        if not match:
            return None
        return match[0]

    @pydantic.validator('elr', pre=True)
    @classmethod
    def strip_strings(cls, value: str) -> Union[str, None]:
        """Strip string"""
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.lower() == 'nan':
            return None
        return stripped

    @classmethod
    @pydantic.validate_arguments
    def factory(cls, line: str) -> Union[object, None]:
        """Instantiate a ELRMapping object from CSV line"""
        if not line.strip():
            return None
        values = line.split('\t')
        if not len(values) == 4:
            return None

        val_dict = {
            'elr': values[0],
            'code': values[3]
        }

        return cls(**val_dict)

def get_elr_mapping() -> list:
    """Parse the CSV, create a list of ELRMapping objects"""

    with open(ELR_MAPPING, 'r', encoding='utf-8') as file:
        return [ELRMapping.factory(line)
                for line in file.readlines() if 'no ELR' not in line]

def get_pride_lor() -> list:
    """Parse the CSV, create a list of LORPride objects"""

    with open(PRIDE_LOR_CODES, 'r', encoding='utf-8') as file:
        return [LORPride.factory(line) for line in file.readlines()]

def update_lor(session: Session) -> None:
    """Update ELR with LOR"""

    pride_lor = get_pride_lor()
    mapping = get_elr_mapping()

    def return_lor(code: str) -> Union[LORPride, None]:
        """Return None or the LORPride object"""
        for obj in pride_lor:
            if obj.code == code:
                return obj
        return None

    for item in mapping:
        lor = return_lor(item.code)
        stmt = f"""
        UPDATE engineerslineref
        SET lor_reference = "{lor.code}",
            lor_name = "{lor.name}",
            ra_value = {lor.ra_value}
        WHERE
            elr = "{item.elr}";
        """.strip()

        session.execute(stmt)

    session.commit()

def main():
    """Entry point if running module"""
    engine = create_engine(DB_CON_STRING, echo=False)
    session = Session(engine)
    SQLModel.metadata.create_all(engine)

    with open(ELR_REFERENCE, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            try:
                session.add(EngineersLineRef.factory(line))
            except pydantic.ValidationError as err:
                print(f"Skipped: {line}\n\t{err}")

    session.commit()
    update_lor(session)

if __name__ == "__main__":
    main()
