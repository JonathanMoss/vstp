"""Functions for importing needed files"""

import os
from pathfinder import Pathfinder
from location_record import LocationRecord
from network_links import NetworkLink
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

    with open(f_name, 'r') as open_file:

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
