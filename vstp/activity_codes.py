""" CIF (BPLAN) ACTIVITY CODES """

from pydantic import BaseModel, Field
from typing import ClassVar, List


class ActivityCode(BaseModel):
    """ Representation of an activity code """
   
    instances: ClassVar[List] = []

    code: str = Field(
        pattern=r"^[A-Z*-x{}]{1,2}$"
    )
    desc: str


    @classmethod
    def factory_from_bplan_entry(cls, entry: str) -> object:
        """ Create an ActivityCode record from a BPLAN entry """

        return cls(
            code=entry[3].strip(),
            desc=entry[4].strip()
        ) 

    @classmethod
    def import_bplan(cls, entries: list) -> None:
        """ Import from a list of BPLAN entries """

        for entry in entries:
            print(entry)
            if 'ACT' not in entry:
                continue

            obj = cls.factory_from_bplan_entry(entry)
            cls.instances.append(obj)
