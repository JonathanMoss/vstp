"""BPLAN Timing Link Record Model"""

from typing import Union
import pydantic


class Tiploc(pydantic.BaseModel):
    """ A representation of a TIPLOC """

    model_config = pydantic.ConfigDict(
        validate_by_name=True
    )

    tiploc: str = pydantic.Field(
        pattern=r"^[A-Z0-9]{3,7}$"
    )

    @classmethod
    @pydantic.validate_call
    def factory(cls, val_tiploc: str):
        return cls(tiploc=val_tiploc)


class TimingLink(pydantic.BaseModel):
    """ A representation of a Timing Link """

    _instances = []

    model_config = pydantic.ConfigDict(
        validate_by_name=True
    )

    start_tiploc: Tiploc
    end_tiploc: Tiploc

    line_code: str = pydantic.Field(
            pattern=r"^[A-Z0-9]{0,3}$",
        )

    traction_type: str = pydantic.Field(
            max_length=6
        )

    trailing_load: str = pydantic.Field(
            pattern=r"^[0-9]{0,4}[A-Z]{0,1}$"
        )

    speed: str = pydantic.Field(
            pattern=r"^[A-Z0-9]{0,3}$"
        )

    ra_guage: str = pydantic.Field(
            pattern=r"^[0-9]{0,3}$"
        )

    entry_speed: str = pydantic.Field(
            pattern=r"[-]{0,1}[0-1]{1}"
        )

    exit_speed: str = pydantic.Field(
            pattern=r"[-]{0,1}[0-1]{1}"
        )

    srt: str = pydantic.Field(
            pattern=r"^[+-]{1}[0-9]{2,3}'[0-9]{2}$"
        )

    @pydantic.field_validator(
        'line_code',
        'trailing_load',
        'ra_guage',
        mode='before')
    @classmethod
    def trim_str(cls, data: str) -> Union[str, None]:
        """ Trim data, return None if blank """
        return data.strip()

    @classmethod
    @pydantic.validate_call
    def factory_from_TLK(cls, val: list):
        return cls(
                start_tiploc=Tiploc.factory(val[2]),
                end_tiploc=Tiploc.factory(val[3]),
                line_code=val[4],
                traction_type=val[5],
                trailing_load=val[6],
                speed=val[7],
                ra_guage=val[8],
                entry_speed=val[9],
                exit_speed=val[10],
                srt=val[13]
            )
