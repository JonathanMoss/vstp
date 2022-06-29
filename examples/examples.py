"""This module contains numerous examples"""

import sys
sys.path.insert(0, './vstp')  # nopep8

from pathfinder import Pathfinder
import bplan_import as f_import

# import the NWK and LOC files - needed only once
f_import.import_location()
f_import.import_network_links()

# Define the path criteria
PATH = Pathfinder('CREWE', 'DRBY')
PATH.search()  # Start the search and output to STDOUT
print()

PATH = Pathfinder('DRBY', 'CREWE')
PATH.search()
print()

path = Pathfinder('CREWE', 'DRBY', via=['STAFFRD'])
path.search()
print()

path = Pathfinder('CREWE', 'DRBY', avoid=['ALSAGER'])
path.search()
print()

path = Pathfinder('PADTON', 'PLYMTH')
path.search()
print()

path = Pathfinder('GLGC', 'EUSTON', via=['SHFD', 'MOTHRWL', 'HUYTON'])
path.search()

print()
path = Pathfinder('GLGC', 'EUSTON', via=['YORK', 'CREWE', 'PNKRDG', 'BHAMNWS', 'NMPTN'])
path.search()

print()
path = Pathfinder('ABRDEEN', 'PENZNCE')
path.search()
