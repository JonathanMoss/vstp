"""Main module for UK rail route path finding"""

# pylint: disable= C0301

from pathfinder import Pathfinder
from location_record import LocationRecord
from network_links import NetworkLink


def import_from_file(f_name: str) -> list:
    """Import the records from a file"""

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


if __name__ == "__main__":

    # import NWK records into memory
    import_network_links()

    # import LOC records into memory
    import_location()

    # PATH = Pathfinder("STAFFRD", "WEAVERJ")
    # PATH = Pathfinder("CREWE", "WEAVERJ", ['CREWECY', 'WNSFD', 'HARTFD', 'ACBG'])
    # PATH = Pathfinder("CREWE", "CREWE", ['CREWECY', 'WNSFD',
    #                                      'HARTFD', 'ACBG', 'WIGANNW', 'LVRPLSH'])
    PATH = Pathfinder("CREWE", "CREWE", ['CREWECY', 'WNSFD',
                                         'HARTFD', 'HARTFDJ', 'ACBG', 'WEAVERJ', 'WIGANNW', 'LVRPLSH'])
    # PATH = Pathfinder("CREWE", "BHAMNWS", ['ALSAGER', 'KIDSGRV', 'LNGP', 'STOKEOT', 'STONE', 'STAFFRD', 'PNKRDG', 'WVRMPTN'])
    # PATH.search()

    # PATH = Pathfinder("CREWE", "CHST", avoid=['CREWESW'])
    #
    # PATH.search()

    # PATH = Pathfinder("CREWBHJ", "ALSAGER", via=['CREWE'])
    # PATH = Pathfinder("EUSTON", "STOKEOT", via=['STAFFRD'], ssd="2021-04-05", odt="13:00:00")
    # PATH.search()
    #
    # PATH = Pathfinder("CREWE", "DRBY")
    #
    PATH.search()
