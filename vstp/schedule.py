"""classes that represent a schedule object"""

from datetime import datetime
from dateutil.parser import parse as dt_parse


def pad_str(data: str, length: int) -> str:
    """Pads a string with spaces to meet the required length"""

    return str(data).ljust(length)


def as_cif_date(cif_date: datetime) -> str:
    """Pass a datetime object, returns YYMMDD"""

    return datetime.strftime(cif_date, '%y%m%d')


def validate_len(data: str, length: list, default: str) -> str:
    """Validates the maximum length of a passed string"""

    if not len(data) in length:
        return default

    return data


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

    def __init__(self, **kwargs):
        """Initialisation"""

        if 'transaction_type' in kwargs:
            self.transaction_type = validate_len(
                kwargs['transaction_type'],
                [1],
                'N'
            )
        else:
            self.transaction_type = 'N'

        self.uid = validate_len(
            kwargs['uid'],
            [5, 6],
            '99999'
        )

        self.date_from = format_date(kwargs['date_from'], True)

        if 'date_to' in kwargs:
            self.date_to = format_date(kwargs['date_to'], True)
        else:
            self.date_to = self.date_from

        if 'days_run' in kwargs:
            self._days_run = validate_len(
                kwargs['days_run'],
                [7],
                '0000000'
            )
        else:
            self._days_run = None

        self.bank_hol = validate_len(
            kwargs.get('bank_hol', ''),
            [1],
            ''
        )

        self.train_status = validate_len(
            kwargs['train_status'],
            [1],
            ''
        )

        self.train_category = validate_len(
            kwargs['train_category'],
            [2],
            'DT'
        )

        self.train_identity = validate_len(
            kwargs['train_identity'],
            [4],
            '9X99'
        )

        if 'headcode' in kwargs:
            self._headcode = validate_len(
                kwargs['headcode'],
                [4],
                '9X99'
            )

        self.service_code = validate_len(
            kwargs['service_code'],
            [8],
            '99999999'
        )

        if 'portion_id' in kwargs:
            self._portion_id = validate_len(
                kwargs['portion_id'],
                [1],
                ''
            )

        self.power_type = validate_len(
            kwargs['power_type'],
            [1, 2, 3],
            'D'
        )
        if 'timing_load' in kwargs:
            self._timing_load = validate_len(
                kwargs['timing_load'],
                [1, 2, 3, 4],
                '9999'
            )

        self.speed = validate_len(
            kwargs['speed'],
            [1, 2, 3],
            '035'
        )

        if 'op_char' in kwargs:
            self._op_char = validate_len(
                kwargs['op_char'],
                [1, 2, 3, 4, 5, 6],
                'Q'
            )

        if 'seating' in kwargs:
            self._seating = validate_len(
                kwargs['seating'],
                [1],
                'B'
            )

        if 'sleepers' in kwargs:
            self._sleepers = validate_len(
                kwargs['sleepers'],
                [1],
                ''
            )

        if 'reservations' in kwargs:
            self._reservations = validate_len(
                kwargs['reservations'],
                [1],
                ''
            )

        if 'catering' in kwargs:
            self._catering = validate_len(
                kwargs['catering'],
                [1, 2, 3, 4],
                ''
            )

        if 'branding' in kwargs:
            self._branding = validate_len(
                kwargs['branding'],
                [1, 2, 3, 4],
                ''
            )

        if 'stp_indicator' in kwargs:
            self._stp_indicator = validate_len(
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

        return ''

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

        return ''

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

        return ''

    @property
    def op_char(self) -> str:
        """Returns the operating characteristics"""

        if hasattr(self, '_op_char'):
            return self._op_char

        return ''

    @property
    def timing_load(self):
        """Returns the service timing load"""

        if hasattr(self, '_timing_load'):
            return self._timing_load

        return ''

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
        line += f'{self.days_run}{pad_str(self.bank_hol, 1)}'
        line += f'{pad_str(self.train_status, 1)}{self.train_category}'
        line += f'{self.train_identity}{self.headcode}'
        line += f'1{pad_str(self.service_code, 8)}{pad_str(self.portion_id, 1)}'
        line += f'{pad_str(self.power_type, 3)}{pad_str(self.timing_load, 4)}'
        line += f'{pad_str(self.speed, 3)}{pad_str(self.op_char, 6)}'
        line += f'{pad_str(self.seating, 1)}{pad_str(self.sleepers, 1)}'
        line += f'{pad_str(self.reservations, 1)}'
        line += f'{SPARE}{pad_str(self.catering, 4)}'
        line += f'{pad_str(self.branding, 4)}{SPARE}{self.stp_indicator}'

        return line


class ExtraSchedule:
    """Representation of a BX record for a schedule"""

    def __init__(self, **kwargs):
        """Initialisation"""

        if 'uic' in kwargs:
            self._uic = validate_len(
                kwargs['uic'],
                [5],
                ''
            )

        self.atoc = validate_len(
            kwargs['atoc'],
            [2],
            'ZZ'
        )

        self.appl = validate_len(
            kwargs['appl'],
            [1],
            'N'
        )

    @property
    def uic(self) -> str:
        """Returns the schedule UIC code"""

        if hasattr(self, '_uic'):
            return self._uic

        return ''

    def __str__(self):
        """Returns a string representation of the BX"""

        line = f'BX{pad_str("", 4)}{pad_str(self.uic, 5)}'
        line += f'{pad_str(self.atoc, 2)}{pad_str(self.appl, 1)}'
        line += f'{pad_str("", 8)}{pad_str("", 1)}{pad_str("", 57)}'
        return line

    @classmethod
    def create_from_string(cls, bx_record: str):
        """Pass a CIF BX record, returns a ExtraSchedule object"""

        if not isinstance(bx_record, str) or not bx_record.startswith('BX'):
            raise ValueError('BX record is not of the required format')

        if not len(bx_record) == 80:
            raise ValueError('BX record is not the required length')

        return cls(**{
            'uic': bx_record[6: 11],
            'atoc': bx_record[11: 13],
            'appl': bx_record[13]
        })


class Schedule:
    """Base schedule"""

    def __init__(self, **kwargs):
        """Initialisation"""


class TimingPoint:
    """Represents each row in a schedule"""

    def __init__(self, **kwargs):
        """Initialisation"""


class LocationOrigin(TimingPoint):
    """Represents a timing point at origin"""

    def __init__(self, **kwargs):
        """Initialisation"""


class LocationIntermediate(TimingPoint):
    """Represents an intermediate timing point"""

    def __init__(self, **kwargs):
        """Initialisation"""


class LocationTerminating(TimingPoint):
    """Represents the terminating timing point"""

    def __init__(self, **kwargs):
        """Initialisation"""
