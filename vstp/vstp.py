#!/bin/python3
"""A command line wrapper for VSTP queries"""

import sys
import os
import argparse
import pydantic
from typing import List
from pathfinder import Pathfinder
import bplan_import as f_import
from location_record import LocationRecord
from sched_models import Schedule
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

class FullTripTable(Table):
    
    HEADERS = ["#", "TIPLOC", "Name", "Mileage", "Path", "Arrive", "Platform", "Depart", "Line", "Activity", "Eng. Allowance", "Perf. Allowance", "Path. Allowance"]
    STYLE = 'bold magenta'
    
    def __init__(self):
        super().__init__(show_header=True, header_style=self.STYLE)
        
        for header in self.HEADERS:
            self.add_column(header)
        
    def _add_row(self, items: list):
        self.add_row(*items)
        
    def populate_table(self, all_items: list):
        for item in all_items:
            self._add_row(item)
            
    def populate_from_schedule(self, schedule: Schedule) -> None:
        for row in schedule.rows:
            self._add_row(row.__dict__.values())

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
        
        self.table.add_column('#')
        self.table.add_column('TIPLOC')
        self.table.add_column('Name')
        self.table.add_column('STANOX')
        self.table.add_column('Timing Point Type')
        self.table.add_column('Lat/Lon')
        
        for key, match in enumerate(results):
            self.table.add_row(
                str(key + 1),
                match.location_code,
                match.location_name,
                match.stanox_code,
                match.timing_point_type,
                str(match.wgs_coordinates)
            )


class LinkSelectTable():
    """"""
    def __init__(self, results):
        ""
        self.table = Table(
            show_header=True,
            header_style="bold magenta",
            
        )
        
        self.table.add_column('#',)
        self.table.add_column('TIPLOC')
        self.table.add_column('Name')
        
        for row in results:

            self.table.add_row(*row)

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
psr.add_argument('--from_loc', type=str, help ='from <TIPLOC> show all linked locations')
psr.add_argument('--find', type=str, help='find TIPLOC')
psr.add_argument('--build', type=str, help='Build a route, provide the first TIPLOC')
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
    
if args.from_loc:
    CONSOLE.print(Markdown(f"# Network Links: ```{args.from_loc}```"))
    results = f_import.NetworkLink.get_neighbours(args.from_loc)
    locs = []
    for result in results:
        rcd = LocationRecord._instances[result]
        locs.append(f'{rcd.location_code}:{rcd.location_name}')
    table = TiplocTable(locs)
    CONSOLE.print(table.table)
    sys.exit(0)
    
if args.build:
    
    links = []
    
    def trip_table(cur_trip: list) -> str:
        locs = []
        for result in cur_trip:
            rcd = LocationRecord._instances[result[1]]
            locs.append(f'{rcd.location_code}:{rcd.location_name}')
        return TiplocTable(locs).table
    
    def get_links(tiploc: str) -> str:
        results = f_import.NetworkLink.get_neighbours(tiploc)
        locs = []
        for index, result in enumerate(results):
            rcd = LocationRecord._instances[result]
            locs.append([str(index + 1), rcd.location_code, rcd.location_name])
        return locs
    
    def get_link(tiploc_a: str, tiploc_b) -> object:
        pass
    
    current_trip = []
    if not LocationRecord.return_instance(args.build):
        CONSOLE.print(Markdown(f"# ERROR, invalid TIPLOC: ```{args.build}```"))
        sys.exit(1)
        
    # insert the origin point into the current trip
    origin = LocationRecord._instances[args.build]
    current_trip.append([len(current_trip), origin.location_code, origin.location_name])
    
    while True and current_trip:
        CONSOLE.clear()
        if len(current_trip) > 1:
            CONSOLE.print(Markdown(f"# Route Builder, START: ```{args.build}```, END: ```{current_trip[-1][1]}```"))
        else:
            CONSOLE.print(Markdown(f"# Route Builder, START: ```{args.build}```"))
        CONSOLE.print(Markdown('## Current Route'))
        CONSOLE.print(trip_table(current_trip))
        links = get_links(current_trip[-1][1])
        CONSOLE.print(Markdown('## Next Location Options'))
        print()
        table = LinkSelectTable(links).table
        CONSOLE.print(table)
        print()
        answer = CONSOLE.input(Markdown(f"# [#] Add TIPLOC from table | [R]emove last entry | e[X]it: "))

        if answer == "X":
            CONSOLE.clear()
            if len(current_trip) > 1:
                CONSOLE.print(Markdown(f"# Route Builder, START: ```{current_trip[0][2]}```, END: ```{current_trip[-1][2]}```"))
            else:
                CONSOLE.print(Markdown(f"# Route Builder, START: ```{args.build}```"))
                CONSOLE.print(Markdown('## Current Route'))
            CONSOLE.print(trip_table(current_trip))
            sys.exit(0)
        if answer == "R" and current_trip:
            current_trip.pop()
        if answer.isnumeric():
            answer = int(answer) - 1
            next_loc = LocationRecord._instances[links[answer][1]]
            current_trip.append([len(current_trip), next_loc.location_code, next_loc.location_name])
        if answer == "M" and len(current_trip) > 1:
            CONSOLE.clear()
            CONSOLE.print(Markdown(f"# Route Builder, START: ```{current_trip[0][2]}```, END: ```{current_trip[-1][2]}```"))
            schedule = Schedule.factory(current_trip)
            tab = FullTripTable()
            schedule.update_mileages(None)
            tab.populate_from_schedule(schedule)
            CONSOLE.print(tab)   

            
            sys.exit()
            
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
