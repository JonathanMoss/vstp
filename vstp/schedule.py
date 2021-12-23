"""classes that represent a schedule object"""

from datetime import datetime
from dateutil.parser import parse as dt_parse


class Schedule:
    """Base schedule"""

    OPT_FIELDS = [
        'bank_hol_running',
        'headcode',
        'portion_id',
        'timing_load',
        'op_char',
        'seating',
        'sleepers',
        'reservations',
        'catering_code',
        'service_branding'
    ]

    def __init__(self, **kwargs):
        """Initialisation"""

        self.transaction_type = 'N'
        self.uid = kwargs['uid']
        self.ssd = Schedule.format_date(kwargs['ssd'], True)
        self.train_status = kwargs['train_status']
        self.train_category = kwargs['train_category']
        self.train_identity = kwargs['headcode']
        self.headcode = kwargs['headcode']
        self.course_indicator = '1'
        self.service_code = kwargs['service_code']
        self.portion_id = ''
        self.power_type = kwargs['power_type']
        self.timing_load = kwargs['timing_load']
        self.speed = kwargs['speed']
        self.op_char = kwargs['op_char']
        self.seating = kwargs['seating']
        self.sleepers = kwargs['sleepers']

        self.stp = 'N'

    @property
    def end_date(self):
        """Returns the schedule end date"""
        return self.ssd

    @property
    def days_run(self) -> str:
        """Returns the days run string"""

        days_run = list('0' * 7)
        days_run[self.ssd.weekday()] = '1'
        return ''.join(days_run)

    @staticmethod
    def format_date(date_str: str, date_only=False) -> datetime:
        """Returns a datetime object for the date/datetime passed"""

        if not isinstance(date_str, str):
            return None

        try:
            parsed = dt_parse(date_str)
        except ValueError as err:
            return None

        if date_only:
            return parsed.date()

        return parsed

    @staticmethod
    def get_days_run(schedule_date: datetime) -> str:
        """Calculates the days run for a given date"""


class TimingPoint:
    """Represents each row in a schedule"""
