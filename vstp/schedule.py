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

    @classmethod
    def create_from_string(cls, bs_record: str):
        """Pass a CIF BS record, returns a BasicSchedule object"""

        if not isinstance(bs_record, str) or not bs_record.startswith('BS'):
            raise ValueError('BS record is not of the required format')

        if not len(bs_record) == 80:
            raise ValueError('BS record is not the required length')

        return cls(**{
            'transaction_type': bs_record[2],
            'uid': bs_record[3: 9],
            'date_from': f'20{bs_record[9: 11]}-{bs_record[11: 13]}-{bs_record[13: 15]}',
            'date_to': f'20{bs_record[15: 17]}-{bs_record[17: 19]}-{bs_record[19: 21]}',
            'days_run': bs_record[21: 28],
            'bank_hol': bs_record[28],
            'train_status': bs_record[29],
            'train_category': bs_record[30: 32],
            'train_identity': bs_record[32: 36],
            'headcode': bs_record[36: 40],
            'service_code': bs_record[41: 49],
            'portion_id': bs_record[49],
            'power_type': bs_record[50: 53],
            'timing_load': bs_record[53: 57],
            'speed': bs_record[57: 60],
            'op_char': bs_record[60: 66],
            'seating': bs_record[66],
            'reservations': bs_record[67],
            'catering': bs_record[69: 73],
            'branding': bs_record[73: 77],
            'stp_indicator': bs_record[79]
        })

    @staticmethod
    def validate_len(data: str, length: list, default: str) -> str:
        """Validates the maximum length of a passed string"""

        if not len(data) in length:
            return default

        return data

    def __init__(self, **kwargs):
        """Initialisation"""

        if 'transaction_type' in kwargs:
            self.transaction_type = BasicSchedule.validate_len(
                kwargs['transaction_type'],
                [1],
                'N'
            )
        else:
            self.transaction_type = 'N'

        self.uid = BasicSchedule.validate_len(
            kwargs['uid'],
            [5, 6],
            '99999'
        )

        self.date_from = Schedule.format_date(kwargs['date_from'], True)

        if 'date_to' in kwargs:
            self.date_to = Schedule.format_date(kwargs['date_to'], True)
        else:
            self.date_to = self.date_from

        if 'days_run' in kwargs:
            self._days_run = BasicSchedule.validate_len(
                kwargs['days_run'],
                [7],
                '0000000'
            )
        else:
            self._days_run = None

        self.bank_hol = BasicSchedule.validate_len(
            kwargs.get('bank_hol', ' '),
            [1],
            ' '
        )

        self.train_status = BasicSchedule.validate_len(
            kwargs['train_status'],
            [1],
            ' '
        )

        self.train_category = BasicSchedule.validate_len(
            kwargs['train_category'],
            [2],
            'DT'
        )

        self.train_identity = BasicSchedule.validate_len(
            kwargs['train_identity'],
            [4],
            '9X99'
        )

        if 'headcode' in kwargs:
            self._headcode = BasicSchedule.validate_len(
                kwargs['headcode'],
                [4],
                '9X99'
            )

        self.service_code = BasicSchedule.validate_len(
            kwargs['service_code'],
            [8],
            '99999999'
        )

        if 'portion_id' in kwargs:
            self._portion_id = BasicSchedule.validate_len(
                kwargs['portion_id'],
                [1],
                ' '
            )

        self.power_type = BasicSchedule.validate_len(
            kwargs['power_type'],
            [1, 2, 3],
            'D  '
        )
        if 'timing_load' in kwargs:
            self._timing_load = BasicSchedule.validate_len(
                kwargs['timing_load'],
                [1, 2, 3, 4],
                '9999'
            )

        self.speed = BasicSchedule.validate_len(
            kwargs['speed'],
            [1, 2, 3],
            '35'
        )

        if 'op_char' in kwargs:
            self._op_char = BasicSchedule.validate_len(
                kwargs['op_char'],
                [1, 2, 3, 4, 5, 6],
                'Q'
            )

        if 'seating' in kwargs:
            self._seating = BasicSchedule.validate_len(
                kwargs['seating'],
                [1],
                ' '
            )

        if 'sleepers' in kwargs:
            self._sleepers = BasicSchedule.validate_len(
                kwargs['sleepers'],
                [1],
                ' '
            )

        if 'reservations' in kwargs:
            self._reservations = BasicSchedule.validate_len(
                kwargs['reservations'],
                [1],
                ' '
            )

        if 'catering' in kwargs:
            self._catering = BasicSchedule.validate_len(
                kwargs['catering'],
                [1, 2, 3, 4],
                '    '
            )

        if 'branding' in kwargs:
            self._branding = BasicSchedule.validate_len(
                kwargs['branding'],
                [1, 2, 3, 4],
                '    '
            )

        if 'stp_indicator' in kwargs:
            self._stp_indicator = BasicSchedule.validate_len(
                kwargs['stp_indicator'],
                [1],
                'N'
            )

    @property
    def stp_indicator(self) -> str:
        """Returns the STP indicator for the service schedule"""

        if hasattr(self, '_stp_indicator'):
            return self._stp_indicator

        return 'N'

    @property
    def portion_id(self) -> str:
        """Return the portion ID indicator for the service"""

        if hasattr(self, '_portion_id'):
            return self._portion_id

        return ' '

    @property
    def days_run(self) -> str:
        """Returns the days run string"""

        if not self._days_run:
            days_run = list('0' * 7)
            days_run[self.date_from.weekday()] = '1'
            return ''.join(days_run)

        return self._days_run

    @property
    def catering(self) -> str:
        """Return catering options"""

        if hasattr(self, '_catering'):
            return self._catering

        return ''

    @property
    def branding(self) -> str:
        """Return service branding"""

        if hasattr(self, '_branding'):
            return self._branding

        return ''

    @property
    def seating(self) -> str:
        """Return seating classes"""

        if self._seating:
            return self._seating

        return ""

    @property
    def sleepers(self) -> str:
        """Return sleeper accomodation"""

        if hasattr(self, '_sleepers'):
            return self._sleepers

        return ''

    @property
    def reservations(self) -> str:
        """Return reservation recommendations"""

        if self._reservations:
            return self._reservations

        return ""

    @property
    def op_char(self) -> str:
        """Returns the operating characteristics"""

        if hasattr(self, '_op_char'):
            return self._op_char

        return '     '

    @property
    def timing_load(self):
        """Returns the service timing load"""

        if hasattr(self, '_timing_load'):
            return self._timing_load

        return '    '

    @property
    def headcode(self) -> str:
        """Returns the schedule headcode"""

        if hasattr(self, '_headcode'):
            return self._headcode

        return self.train_identity

    def __str__(self):
        """Return a string representation of the BS"""

        SPARE = ' '
        line = f'BS{self.transaction_type}{pad_str(self.uid, 6)}'
        line += f'{as_cif_date(self.date_from)}{as_cif_date(self.date_to)}'
        line += f'{self.days_run}{self.bank_hol}'
        line += f'{self.train_status}{self.train_category}'
        line += f'{self.train_identity}{self.headcode}'
        line += f'1{pad_str(self.service_code, 8)}{self.portion_id}'
        line += f'{pad_str(self.power_type, 3)}{pad_str(self.timing_load, 4)}'
        line += f'{pad_str(self.speed, 3)}{pad_str(self.op_char, 6)}'
        line += f'{self.seating}{self.sleepers}{self.reservations}'
        line += f'{SPARE}{pad_str(self.catering, 4)}'
        line += f'{pad_str(self.branding, 4)}{SPARE}{self.stp_indicator}'

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
