#!/bin/python3
"""A command line wrapper for VSTP queries"""

import sys
import os
import argparse
from pathfinder import Pathfinder
import bplan_import as f_import
from location_record import LocationRecord

# import the NWK and LOC files - needed only once
f_import.import_location()
f_import.import_network_links()

psr = argparse.ArgumentParser(
    prog='vstp',
    description='Runs VSTP style path queries',
    epilog='...a work in progress'
)
psr.add_argument('--start', type=str, help='The start TIPLOC')
psr.add_argument('--end', type=str, help='The end TIPLOC')
psr.add_argument('--via', type=str, help='"TIPLOC, TIPLOC, ..." via location(s)')
psr.add_argument('--avoid', type=str, help='"TIPLOC, TIPLOC, ..." avoid location(s)')
psr.add_argument(
    '--legs',
    action='store_true',
    default=False,
    help='Show output as grouped legs between via TIPLOCS'
)
psr.add_argument('--find', help='find TIPLOC')
args = psr.parse_args()

os.system('clear')

if args.find:

    results = LocationRecord.match_locations(args.find)
    if results:
        for result in results:
            print(result.split(':'))
    sys.exit(0)

via = []
avoid = []

if args.via:
    via = [tpl.strip() for tpl in args.via.split(',')]

if args.avoid:
    avoid = [tpl.strip() for tpl in args.avoid.split(',')]

path = Pathfinder(args.start, args.end, legs=args.legs, via=via, avoid=avoid)
path.search()
