"""Module to create and manipulate a representation of a timing load"""

import json


class TimingLoad:

    _instance = []

    def __init__(self, *args):
        """Initialisation"""

        self.traction_type = args[2].strip()

        self.trailing_load = args[3].strip()
        if not self.trailing_load:
            self.trailing_load = "N/A"

        speed = args[4].strip()
        if not speed:
            speed = 0
        self.speed = int(speed)

        self.ra = args[5].strip()
        if not self.ra:
            self.ra = "N/A"

        self.description = args[6]
        self.power_type = args[7].strip()  # ITPS Power Type

        self.load = args[8].strip()  # ITPS Timing Load
        if not self.load:
            self.load = "N/A"

        lim_speed = args[9].strip()
        if not lim_speed:
            self.limiting_speed = "N/A"
        else:

            self.limiting_speed = int(lim_speed)

        TimingLoad._instance.append(self)

    @property
    def as_dict(self):
        """Return a dictionary representation of the object"""

        return {
            'traction_type': self.traction_type,
            'trailing_load': self.trailing_load,
            'speed': self.speed,
            'ra': self.ra,
            'description': self.description,
            'power_type': self.power_type,
            'load': self.load,
            'limiting_speed': self.limiting_speed
        }

    def __repr__(self):
        """Return a string representation of the object"""

        return json.dumps(self.as_dict, indent=4)

    @staticmethod
    def match_power(power_type: str, iter_=None):
        """Return a list of all power type matches"""

        ret_list = []

        if not iter_:
            iter_ = TimingLoad._instance

        for instance in iter_:
            if instance.power_type == power_type:
                ret_list.append(instance)

        return ret_list

    @staticmethod
    def match_timing_load(timing_load: str, iter_=None):
        """Returns a list of all timing load matches"""

        ret_list = []

        if not iter_:
            iter_ = TimingLoad._instance

        for instance in iter_:
            if instance.load == timing_load:
                ret_list.append(instance)

        return ret_list
