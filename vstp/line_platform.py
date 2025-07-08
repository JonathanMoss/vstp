""" Models of lines/platform record from BPLAN """

from pydantic import BaseModel, Field
from typing import Union, List, ClassVar

class LinePlatform(BaseModel):
    """ Model of a line/platform record from BPLAN """

    instances: ClassVar[dict] = {}

    tiploc: str = Field(
        pattern=r'^[A-Z0-9]{3,7}$'
    )

    ln_plt: List = Field(
        default=[]
    )

    @classmethod
    def factory_from_bplan_entry(cls, entry: list) -> None:
        """ Takes a entry (line) from PLT and creates object """

        tiploc = entry[2]
        lne_plt = entry[3]

        record = cls.instances.get(tiploc, None)
        if record:
            record.ln_plt.append(lne_plt)
            return

        record = cls(tiploc=tiploc, ln_plt=[lne_plt])
        cls.instances[tiploc] = record

    @classmethod
    def get_all_lines(cls, tiploc: str, as_list: False) -> Union[object, list, None]:
        """ Pass a TIPLOC, get matching record or a list of line/platforms """

        match = cls.instances.get(tiploc, None)

        if not match:
            return None

        if as_list:
            return match.ln_plt

        return match 
    
    @classmethod
    def is_valid(cls, tiploc: str, lne_plt: str) -> bool:
        """ Checks is a line/platform/path is valid for the specified location """
        return lne_plt in cls.instances.get(tiploc).lne_plt
