"""Imports the timing load data into a database"""

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from database.schema import TimingLoad, BASE as Base
from bplan_import import import_from_file

ENGINE = create_engine('sqlite:///tld.db', echo=False)
SESSION = sessionmaker(bind=ENGINE)()


def strip_value(value: str) -> str:
    """Strips a value, returns value or None"""

    val = value.strip()
    if not val:
        val = None
    return val


def import_timing_loads():
    """Imports the timing load records into a database"""

    Base.metadata.create_all(ENGINE, checkfirst=True)

    with SESSION as ses:

        for record in import_from_file('TLD'):
            if not len(record) == 10:
                continue
            tld = TimingLoad()
            tld.traction_type = strip_value(record[2])
            tld.trailing_load = strip_value(record[3])
            tld.max_speed = strip_value(record[4])
            tld.ra_guage = strip_value(record[5])
            tld.description = strip_value(record[6])
            tld.power_type = strip_value(record[7])
            tld.load = strip_value(record[8])
            tld.limiting_speed = strip_value(record[9])
            try:
                ses.add(tld)
                ses.commit()
            except IntegrityError as err:
                print(record)
                print(err)
                ses.rollback()


if __name__ == '__main__':
    import_timing_loads()
