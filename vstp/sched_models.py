"""VSTP schedule models"""

from typing import List, Union
import pydantic
from network_links import NetworkLink
from location_record import LocationRecord

class ScheduleEntry(pydantic.BaseModel):
    """A representation of a VSTP schedule entry"""
    
    index: str
    tiploc: str
    name: str
    mileage: str = pydantic.Field(default='0')
    path: str = pydantic.Field(default='')
    arr: str = pydantic.Field(default='')
    platform: str = pydantic.Field(default='')
    dep: str = pydantic.Field(default='')
    line: str = pydantic.Field(default='')
    activity: str = pydantic.Field(default='')
    engi_a: str = pydantic.Field(default='')
    perf_a: str = pydantic.Field(default='')
    path_a: str = pydantic.Field(default='')

    lpb: str = pydantic.Field(default='')
    
    @classmethod
    def factory(cls, data: list) -> object:
        """Used to create a ScheduleEntry Object from raw data"""
        return cls(
            index=str(data[0]),
            tiploc=data[1],
            name=data[2]
        )
    
class Schedule(pydantic.BaseModel):
    """A representation of a VSTP schedule"""
    rows: List[ScheduleEntry]
   
    @classmethod
    def factory(cls, raw_schedule: list) -> object:
        """Returns a Schedule Object"""
        
        rows = []
        for index, entry in enumerate(raw_schedule):
            if not isinstance(entry, list):
                entry = [index, entry, ""]
            rows.append(ScheduleEntry.factory(entry))
        return cls(rows=rows)
    
    def get_geo_distance(self, tiploc_a, tiploc_b) -> str:
        """Returns the geographical distance"""
        tiploc_a = LocationRecord.return_instance(tiploc_a)
        tiploc_b = LocationRecord.return_instance(tiploc_b)
        dst = LocationRecord.distance(tiploc_a.wgs_coordinates, tiploc_b.wgs_coordinates)
        dst = dst * 1609.344
        ret_val = str(int(round((dst), 0)))
        return ret_val
    
    
    def update_mileages(self, func: object) -> None:
        """func represents the object to extrapolate the mileages"""
        
        def get_measured_link(links: list) -> Union[int, None]:
            for ind, link in enumerate(links):
                if link.distance.isnumeric():
                    return ind

        previous_tiploc = None
        previous_mileage = 0
        
        for row in self.rows:
            if int(row.index) == 0:
                row.mileage = '0'
                previous_tiploc = row.tiploc
                previous_mileage = 0
                continue
            
            if not float(row.mileage):

                
                links = NetworkLink.get_link(previous_tiploc, row.tiploc)
                index = get_measured_link(links)
                link = links[index]

                if not int(link.distance) or int(link.distance) == 1:
                    link.distance = self.get_geo_distance(previous_tiploc, row.tiploc)
                distance = int(link.distance) + previous_mileage
                previous_mileage = distance
                conv = round((distance / 1000) * 0.621371, 2)
                row.mileage = str(conv)
                previous_tiploc = row.tiploc
            
 
    def extrapolate_lp(self) -> None:
        """ Extrapolate missing line/path from some values """

        for index, row in enumerate(self.rows):
            try:
                if row.line and not self.rows[index + 1].path:

                    self.rows[index + 1].path = row.line
            except IndexError:
                continue

    def default_activities(self) -> None:
        """ Input default activity codes """
        if not self.rows[0].activity:
            self.rows[0].activity = "TB"
        index = len(self.rows) - 1
        if not self.rows[index].activity:
            self.rows[index].activity = 'TF'

    def extrapolate_lp_defaults(self) -> None:
        """ See if there are any single options for lines/paths """

        cur_tpl = ''
        next_tpl = ''

        for index, row in enumerate(self.rows):
            pass

