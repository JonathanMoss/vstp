#!/bin/python3
"""A command line wrapper for VSTP queries"""

import argparse
from pathfinder import Pathfinder
import bplan_import as f_import

# import the NWK and LOC files - needed only once
f_import.import_location()
f_import.import_network_links()

psr = argparse.ArgumentParser()
psr.add_argument('start', type=str, help='The start TIPLOC')
psr.add_argument('end', type=str, help='The end TIPLOC')
psr.add_argument('--via', type=str, help='"TIPLOC, TIPLOC, ..." via location(s)')
psr.add_argument('--avoid', type=str, help='"TIPLOC, TIPLOC, ..." avoid location(s)')
args = psr.parse_args()

via = []
avoid = []

if args.via:
    via = [tpl.strip() for tpl in args.via.split(',')]

if args.avoid:
    avoid = [tpl.strip() for tpl in args.avoid.split(',')]

path = Pathfinder(args.start, args.end, via=via, avoid=avoid)
path.search()
