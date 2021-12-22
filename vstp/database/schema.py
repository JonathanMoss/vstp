"""Database models for BPLAN records"""

# pylint: disable=R0903
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer
BASE = declarative_base()


class TimingLoad(BASE):
    """Represents a timing load record from BPLAN"""

    __tablename__ = 'timing_loads'

    id = Column(Integer, primary_key=True)
    traction_type = Column(String(6), nullable=False)
    trailing_load = Column(String(5), nullable=True)
    max_speed = Column(String(3), nullable=False)
    ra_guage = Column(String(3), nullable=True)
    description = Column(String(64), nullable=False)
    power_type = Column(String(3), nullable=True)
    load = Column(String(4), nullable=True)
    limiting_speed = Column(String(3), nullable=True)
