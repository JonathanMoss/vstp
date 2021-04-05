"""Main module for UK rail route path finding"""

from pathfinder import Pathfinder
from location_record import LocationRecord
from network_links import NetworkLink
from timing_load import TimingLoad


def import_from_file(f_name: str) -> list:
    """Import the records from a file"""

    ret_list = []

    with open(f_name, 'r') as open_file:

        for line in open_file:
            split_ln = line.replace('\n', '')
            split_ln = split_ln.split('\t')

            if len(split_ln) > 1:
                ret_list.append(split_ln)

    return ret_list


def import_location():
    """Import the location records from the file"""

    locs = []
    for loc_record in import_from_file('LOC'):
        locs.append(LocationRecord(*loc_record))

    return locs


def import_timing_loads():
    """Import the timing loads (TLD) from the file"""

    tlds = []
    for load in import_from_file('TLD'):
        tlds.append(TimingLoad(*load))

    return tlds


def import_network_links():
    """Import the network link records from the NWK file"""

    for link in import_from_file('NWK'):

        lnk = NetworkLink(*link)
        rlc = str(lnk.running_line_code).upper()
        rld = str(lnk.running_line_description).upper()

        if 'BUS' in (rlc, rld):
            continue

        lnk.append_to_instance()


if __name__ == "__main__":

    # Import Timing Loads
    import_timing_loads()

    pwr_match = TimingLoad.match_power('HST')
    full_match = TimingLoad.match_timing_load('125', pwr_match)
    print(full_match)

    # # import LOC records into memory
    # import_location()
    #
    # # import NWK records into memory
    # import_network_links()
    #
    # PATH = Pathfinder("EUSTON", "STOKEOT", via=['STAFFRD'], ssd="2021-04-05", odt="13:00:00")
    # PATH.search()
