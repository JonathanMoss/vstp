#!/bin/python3
"""A command line wrapper for VSTP queries"""

import sys
import os
import argparse
from pathfinder import Pathfinder
import bplan_import as f_import
from location_record import LocationRecord
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

# import the NWK and LOC files - needed only once
f_import.import_location()
f_import.import_network_links()

CONSOLE=Console()

NO_ARGS="""
# User Error
Missing arguments, please run ```python3 vstp.py --help```
""".strip()

class RouteRequestTable():
    """"""
    
    def __init__(self, start: str, end: str, via: list=None, avoid: list=None):
        ""
        self.grid = Table.grid(expand=False)
        self.grid.add_column(style="bold magenta", width=20)
        self.grid.add_column()
        self.grid.add_row("Start TIPLOC", start)
        self.grid.add_row("End TIPLOC", end)
        
        if via:
            self.grid.add_row("via TIPLOC(S)", via)
        if avoid:
            self.grid.add_row("avoid TIPLOC(S)", avoid)

class TiplocTable():
    """"""
    def __init__(self, results):
        ""
        self.table = Table(
            show_header=True,
            header_style="bold magenta",
            
        )
        
        self.table.add_column('TIPLOC')
        self.table.add_column('Name')
        
        for row in results:
            self.table.add_row(*row.split(':'))

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

if not any(args.__dict__.values()):
    CONSOLE.print(Markdown(NO_ARGS))
    exit()  
    
if args.find:
    CONSOLE.print(Markdown(f"# TIPLOC search: ```{args.find}```"))
    results = LocationRecord.match_locations(args.find)
    table = TiplocTable(results)
    CONSOLE.print(table.table)
    sys.exit(0)

via = []
avoid = []

if args.via:
    via = [tpl.strip() for tpl in args.via.split(',')]

if args.avoid:
    avoid = [tpl.strip() for tpl in args.avoid.split(',')]
    
CONSOLE.print(Markdown(f"# VSTP query"))
CONSOLE.print(RouteRequestTable(args.start, args.end, args.via, args.avoid).grid)


path = Pathfinder(args.start, args.end, legs=args.legs, via=via, avoid=avoid)
path.search(std_out=False)

CONSOLE.print(Markdown("# Results"))
for index, result in enumerate(path.route_locations):
    CONSOLE.print(str(index + 1).zfill(3), result)
