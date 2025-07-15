"""Functions for importing needed files"""

import os
from location_record import LocationRecord
from network_links import NetworkLink
from timing_links import TimingLink
from line_platform import LinePlatform
from activity_codes import ActivityCode
from err import MissingPartFile


def does_file_exist(f_name: str) -> bool:
    """Check if the file exists in the current path"""

    if os.path.isfile(f_name):
        return True

    return False


def import_from_file(f_name: str) -> list:
    """Import the records from a file"""

    if not does_file_exist(f_name):
        raise MissingPartFile(f_name)

    ret_list = []

    with open(f_name, 'r', encoding='utf-8') as open_file:

        for line in open_file:
            split_ln = line.split('\t')
            ret_list.append(split_ln)

    return ret_list


def import_location() -> list:
    """Import the location records from the file"""

    locs = []
    for loc_record in import_from_file('LOC'):
        locs.append(LocationRecord(*loc_record))

    return locs


def import_network_links() -> list:
    """Import the network link records from the NWK file"""

    nwks = []

    for link in import_from_file('NWK'):

        lnk = NetworkLink(*link)
        rlc = str(lnk.running_line_code).upper()
        rld = str(lnk.running_line_description).upper()

        if 'BUS' in (rlc, rld):
            continue

        lnk.append_to_instance()
        nwks.append(lnk)

    return nwks

def import_timing_links() -> list:
    """Import the timing link records from the TLK file"""

    tlks = []
    for link in import_from_file('TLK'):

        lnk = TimingLink.factory_from_TLK(link.split('\t'))
        tlks.append(lnk)

        
    return tlks

def import_line_platform() -> dict:
    """Import the line/platform records from PLT file """

    for entry in import_from_file('PLT'):
        LinePlatform.factory_from_bplan_entry(entry)

    return LinePlatform.instances

def import_activity_codes() -> None:
    """ Import the activity codes """

    ActivityCode.import_bplan(import_from_file('ACT'))