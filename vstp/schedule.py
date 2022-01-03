"""classes that represent a schedule object"""

# pylint: disable=R0902, R0912, R0903

import re
from datetime import datetime
from dateutil.parser import parse as dt_parse


def extrapolate_allowance(allowance: str) -> int:
    """Pass a CIF allowance string, returns an int representing seconds allowance"""

    total = 0

    if not isinstance(allowance, str) or not allowance:
        return total

    if len(allowance) > 2:
        return total

    if 'H' in allowance:
        total += 30
        allowance = allowance.strip('H')

    try:
        total += int(allowance.strip()) * 60
        return total
    except ValueError:
        return total


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
    except ValueError:
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

        spare = ' '
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
        line += f'{spare}{pad_str(self.catering, 4)}'
        line += f'{pad_str(self.branding, 4)}{spare}{self.stp_indicator}'

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

        self.basic_schedule = kwargs['basic_schedule']
        self.extra_schedule = kwargs['extra_schedule']
        self.origin = kwargs['origin']
        self.intermediates = kwargs['intermediates']
        self.terminating = kwargs['terminating']

    @staticmethod
    def return_bs(schedule: str) -> object:
        """Pass a schedule, returns a BasicSchedule object"""

        bs_record = re.search('BS[0-9A-Z ]{78}', schedule)
        if bs_record:
            return BasicSchedule.create_from_string(bs_record.group(0))

        return None

    @staticmethod
    def return_bx(schedule: str) -> object:
        """Pass a schedule, returns a ExtraSchedule object"""

        bx_record = re.search('BX[0-9A-Z ]{78}', schedule)
        if bx_record:
            return ExtraSchedule.create_from_string(bx_record.group(0))

        return None

    @staticmethod
    def return_lo(schedule: str) -> object:
        """Pass the schedule, returns a LocationOrigin object"""

        loc_o = re.search('LO[0-9A-Z ]{78}', schedule)
        if loc_o:
            return LocationOrigin.create_from_string(loc_o.group(0))

        return None

    @staticmethod
    def return_lt(schedule: str) -> object:
        """Pass the schedule, returns a LocationTerminating object"""

        loc_t = re.search('LT[0-9A-Z ]{78}', schedule)
        if loc_t:
            return LocationTerminating.create_from_string(loc_t.group(0))

        return None

    @staticmethod
    def return_li(schedule: str) -> list:
        """Pass the schedule, returns a list of LocationIntermediate objects"""

        res = []

        for record in re.finditer('LI[0-9A-Z ]{78}', schedule):
            res.append(LocationIntermediate.create_from_string(record.group(0)))

        return res

    @classmethod
    def create_from_string(cls, schedule: str) -> object:
        """Pass a correctly formatted string containing a CIF schedule record,
        returns a Schedule object"""

        return cls(**{
            'basic_schedule': Schedule.return_bs(schedule),
            'extra_schedule': Schedule.return_bx(schedule),
            'origin': Schedule.return_lo(schedule),
            'intermediates': Schedule.return_li(schedule),
            'terminating': Schedule.return_lt(schedule),

        })


class TimingPoint:
    """Represents each row in a schedule"""

    def __init__(self, **kwargs):
        """Initialisation"""

        self.tiploc = validate_len(
            kwargs['tiploc'],
            [3, 4, 5, 6, 7],
            ''
        )

        self._suffix = validate_len(
            kwargs['suffix'],
            [1],
            '1'
        )

        if 'wta' in kwargs:
            self._raw_wta = kwargs['wta']
            self._wta = TimingPoint.get_time(self._raw_wta)

        if 'wtp' in kwargs:
            self._raw_wtp = kwargs['wtp']
            self._wtp = TimingPoint.get_time(self._raw_wtp)

        if 'wtd' in kwargs:
            self._raw_wtd = kwargs['wtd']
            self._wtd = TimingPoint.get_time(self._raw_wtd)

        if 'pta' in kwargs:
            self._raw_pta = kwargs['pta']
            self._pta = TimingPoint.get_time(self._raw_pta)

        if 'ptd' in kwargs:
            self._raw_ptd = kwargs['ptd']
            self._ptd = TimingPoint.get_time(self._raw_ptd)

        if 'plt' in kwargs:
            self._platform = validate_len(
                kwargs['plt'],
                [1, 2, 3],
                'TBC'
            )

        if 'line' in kwargs:
            self._line = validate_len(
                kwargs['line'],
                [1, 2, 3],
                ''
            )

        if 'path' in kwargs:
            self._path = validate_len(
                kwargs['path'],
                [1, 2, 3],
                ''
            )

        if 'eng_all' in kwargs:
            self._eng_all = validate_len(
                kwargs['eng_all'],
                [1, 2],
                ''
            )

        if 'pathing_all' in kwargs:
            self._pathing_all = validate_len(
                kwargs['pathing_all'],
                [1, 2],
                ''
            )

        if 'perf_all' in kwargs:
            self._perf_all = validate_len(
                kwargs['perf_all'],
                [1, 2],
                ''
            )

        self.activity = validate_len(
            kwargs['act'],
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            ''
        )

    @staticmethod
    def get_time(time_value: str) -> str:
        """Strips the time and convers to datetime"""

        if not isinstance(time_value, str) or not time_value.strip():
            return None

        val = f'{time_value[0: 2]}:{time_value[2: 4]}'
        if 'H' in time_value:
            val += ":30"
        else:
            val += ":00"

        val = format_date(val).time()

        return val

    @property
    def engineering_allowance(self) -> int:
        """Return the engineering allowance in seconds"""

        if hasattr(self, '_eng_all'):
            return extrapolate_allowance(self._eng_all)

        return 0

    @property
    def engineering_allowance_raw(self) -> str:
        """Return the engineering allowance as passed at init"""

        if hasattr(self, '_eng_all'):
            return self._eng_all

        return ''

    @property
    def pathing_allowance(self) -> int:
        """Return the pathing allowance in seconds"""

        if hasattr(self, '_pathing_all'):
            return extrapolate_allowance(self._pathing_all)

        return 0

    @property
    def pathing_allowance_raw(self) -> str:
        """Return the pathing allowance as passed at init"""

        if hasattr(self, '_pathing_all'):
            return self._pathing_all

        return ''

    @property
    def performance_allowance(self) -> int:
        """Return the performance allowance in seconds"""

        if hasattr(self, '_perf_all'):
            return extrapolate_allowance(self._perf_all)

        return 0

    @property
    def performance_allowance_raw(self) -> str:
        """Return the performance allowance as passed at init"""

        if hasattr(self, '_perf_all'):
            return self._perf_all

        return ''

    @property
    def platform(self) -> str:
        """Return the planned platform"""

        if hasattr(self, '_platform'):
            return self._platform

        return 'TBC'

    @property
    def line(self) -> str:
        """Return the planned line out"""

        if hasattr(self, '_line'):
            return self._line

        return ''

    @property
    def path(self) -> str:
        """Return the planned path in"""

        if hasattr(self, '_path'):
            return self._path

        return ''

    @property
    def suffix(self) -> str:
        """Returns the suffix"""

        if not self._suffix:
            return '1'

        return self._suffix

    @property
    def raw_wtd(self) -> str:
        """Return the wtd as provided at init"""

        if hasattr(self, '_raw_wtd'):
            return self._raw_wtd

        return ""

    @property
    def raw_wtp(self) -> str:
        """Return the wtp as provided at init"""

        if hasattr(self, '_raw_wtp'):
            return self._raw_wtp

        return ""

    @property
    def raw_wta(self) -> str:
        """Return the wta as provided at init"""

        if hasattr(self, '_raw_wta'):
            return self._raw_wta

        return ""

    @property
    def raw_pta(self) -> str:
        """Return the pta as provided at init"""

        if hasattr(self, '_raw_pta'):
            return self._raw_pta

        return ""

    @property
    def raw_ptd(self) -> str:
        """Return the ptd as provided at init"""

        if hasattr(self, '_raw_ptd'):
            return self._raw_ptd

        return ""


class LocationOrigin(TimingPoint):
    """Represents a timing point at origin"""

    @classmethod
    def create_from_string(cls, lo_record: str):
        """Pass a CIF LO record, returns a LocationOrigin object"""

        if not isinstance(lo_record, str) or not lo_record.startswith('LO'):
            raise ValueError('LO record is not of the required format')

        if not len(lo_record) == 80:
            raise ValueError('LO record is not the required length')

        return cls(**{
            'tiploc': lo_record[2: 9],
            'suffix': lo_record[9],
            'wtd': lo_record[10: 15],
            'ptd': lo_record[15: 19],
            'plt': lo_record[19: 22],
            'line': lo_record[22: 25],
            'eng_all': lo_record[25: 27],
            'pathing_all': lo_record[27: 29],
            'act': lo_record[29: 41],
            'perf_all': lo_record[41: 43]
        })

    def __str__(self) -> str:
        """Return a string representation of the LO"""

        line = f'LO{pad_str(self.tiploc, 7)}{pad_str(self.suffix, 1)}'
        line += f'{pad_str(self.raw_wtd, 5)}{pad_str(self.raw_ptd, 4)}'
        line += f'{pad_str(self.platform, 3)}{pad_str(self.line, 3)}'
        line += f'{pad_str(self.engineering_allowance_raw, 2)}'
        line += f'{pad_str(self.pathing_allowance_raw, 2)}'
        line += f'{pad_str(self.activity, 12)}'
        line += f'{pad_str(self.performance_allowance_raw, 2)}'
        line += f'{pad_str("", 37)}'

        return line


class LocationIntermediate(TimingPoint):
    """Represents an intermediate timing point"""

    @classmethod
    def create_from_string(cls, li_record: str):
        """Pass a CIF LI record, returns a LocationIntermediate object"""

        if not isinstance(li_record, str) or not li_record.startswith('LI'):
            raise ValueError('LI record is not of the required format')

        if not len(li_record) == 80:
            raise ValueError('LI record is not the required length')

        return cls(**{
            'tiploc': li_record[2: 9],
            'suffix': li_record[9],
            'wta': li_record[10: 15],
            'wtd': li_record[15: 20],
            'wtp': li_record[20: 25],
            'pta': li_record[25: 29],
            'ptd': li_record[29: 33],
            'plt': li_record[33: 36],
            'line': li_record[36: 39],
            'path': li_record[40: 42],
            'act': li_record[42: 54],
            'eng_all': li_record[54: 56],
            'pathing_all': li_record[56: 58],
            'perf_all': li_record[58: 60]
        })

    def __str__(self) -> str:
        """Return a string representation of the LI"""

        line = f'LI{pad_str(self.tiploc, 7)}{pad_str(self.suffix, 1)}'
        line += f'{pad_str(self.raw_wta, 5)}{pad_str(self.raw_wtd, 5)}'
        line += f'{pad_str(self.raw_wtp, 5)}{pad_str(self.raw_pta, 4)}'
        line += f'{pad_str(self.raw_ptd, 4)}'
        line += f'{pad_str(self.platform, 3)}{pad_str(self.line, 3)}'
        line += f'{pad_str(self.path, 3)}{pad_str(self.activity, 12)}'
        line += f'{pad_str(self.engineering_allowance_raw, 2)}'
        line += f'{pad_str(self.pathing_allowance_raw, 2)}'
        line += f'{pad_str(self.performance_allowance_raw, 2)}'
        line += f'{pad_str("", 20)}'

        return line


class LocationTerminating(TimingPoint):
    """Represents the terminating timing point"""

    @classmethod
    def create_from_string(cls, lt_record: str):
        """Pass a CIF LT record, returns a LocationTerminating object"""

        if not isinstance(lt_record, str) or not lt_record.startswith('LT'):
            raise ValueError('LT record is not of the required format')

        if not len(lt_record) == 80:
            raise ValueError('LT record is not the required length')

        return cls(**{
            'tiploc': lt_record[2: 9],
            'suffix': lt_record[9],
            'wta': lt_record[10: 15],
            'pta': lt_record[15: 19],
            'plt': lt_record[19: 22],
            'path': lt_record[22: 25],
            'act': lt_record[25: 37]
        })

    def __str__(self) -> str:
        """Return a string representation of the LT"""

        line = f'LT{pad_str(self.tiploc, 7)}{pad_str(self.suffix, 1)}'
        line += f'{pad_str(self.raw_wta, 5)}'
        line += f'{pad_str(self.raw_pta, 4)}'
        line += f'{pad_str(self.platform, 3)}'
        line += f'{pad_str(self.path, 3)}{pad_str(self.activity, 12)}'
        line += f'{pad_str("", 43)}'

        return line
