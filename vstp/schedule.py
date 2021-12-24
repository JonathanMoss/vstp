"""classes that represent a schedule object"""

from datetime import datetime
from dateutil.parser import parse as dt_parse


def pad_str(data: str, length: int) -> str:
    """Pads a string with spaces to meet the required length"""

    return str(data).ljust(length)


def as_cif_date(cif_date: datetime) -> str:
    """Pass a datetime object, returns YYMMDD"""

    return datetime.strftime(cif_date, '%y%m%d')


class BasicSchedule:
    """Contains the Basic Schedule (BX) records"""

    def __init__(self, **kwargs):
        """Initialisation"""

        self.uid = kwargs['uid']
        self.date_from = Schedule.format_date(kwargs['sched_date'], True)
        self._bank_hol = kwargs.get('bank_hol', None)
        self.train_status = kwargs['train_status']
        self.train_category = kwargs['train_category']
        self.train_identity = kwargs['train_identity']
        self.service_code = kwargs['service_code']
        self.power_type = kwargs['power_type']
        self._timing_load = kwargs.get('timing_load', None)
        self.speed = kwargs['speed']
        self._op_char = kwargs.get('op_char', None)
        self._seating = kwargs.get('seating', None)
        self._sleepers = kwargs.get('sleepers', None)
        self._reservations = kwargs.get('reservations', None)
        self._catering = kwargs.get('catering', None)
        self._branding = kwargs.get('branding', None)

    @property
    def days_run(self) -> str:
        """Returns the days run string"""

        days_run = list('0' * 7)
        days_run[self.date_from.weekday()] = '1'
        return ''.join(days_run)

    @property
    def catering(self) -> str:
        """Return catering options"""

        if self._catering:
            return self._catering

        return ""

    @property
    def branding(self) -> str:
        """Return service branding"""

        if self._branding:
            return self._branding

        return ""

    @property
    def seating(self) -> str:
        """Return seating classes"""

        if self._seating:
            return self._seating

        return ""

    @property
    def sleepers(self) -> str:
        """Return sleeper accomodation"""

        if self._sleepers:
            return self._sleepers

        return ""

    @property
    def reservations(self) -> str:
        """Return reservation recommendations"""

        if self._reservations:
            return self._reservations

        return ""

    @property
    def op_char(self) -> str:
        """Returns the operating characteristics"""

        if self._op_char:
            return self._op_char

        return ""

    @property
    def date_to(self) -> datetime:
        """Returns the end date of the schedule"""

        return self.date_from

    @property
    def bank_hol(self) -> str:
        """Returns the bank holiday running char"""

        if self._bank_hol:
            return self._bank_hol

        return ""

    @property
    def timing_load(self):
        """Returns the service timing load"""

        if self._timing_load:
            return self._timing_load

        return ""

    @property
    def headcode(self) -> str:
        """Returns the schedule headcode"""

        return self.train_identity

    def __str__(self):
        """Return a string representation of the BS"""

        line = f'BSN{pad_str(self.uid, 6)}'
        line += f'{as_cif_date(self.date_from)}{as_cif_date(self.date_to)}'
        line += f'{self.days_run}{self.bank_hol}'
        line += f'{self.train_status}{self.train_category}'
        line += f'{self.train_identity}{self.headcode}'
        line += f'1{pad_str(self.service_code, 8)} '
        line += f'{pad_str(self.power_type, 3)}{pad_str(self.timing_load, 4)}'
        line += f'{pad_str(self.speed, 3)}{pad_str(self.op_char, 6)}'
        line += f'{self.seating}{self.sleepers}{self.reservations} '
        line += f'{pad_str(self.catering, 4)}'
        line += f'{pad_str(self.branding, 4)} N'

        return line


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
