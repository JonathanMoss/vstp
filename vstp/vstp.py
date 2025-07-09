#!/bin/python3
"""A command line wrapper for VSTP queries"""

# pylint: disable=E0401, W0621, R0903, W0212

import sys
import os
import argparse
from enum import Enum
from typing import List, Union
from pathfinder import Pathfinder
from network_links import NetworkLink
import bplan_import as f_import
from location_record import LocationRecord
from line_platform import LinePlatform
from sched_models import Schedule
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.style import Style
from rich.prompt import Confirm
from jinja2 import Template

# import the BPLAN files - needed only once
f_import.import_location()
f_import.import_network_links()
f_import.import_line_platform()

CONSOLE = Console()

NO_ARGS = """
# User Error
Missing arguments, please run ```python3 vstp.py --help```
""".strip()

EDIT_SCHEDULE = Markdown('# Edit: [p#]ath | [P#]latform | [L#]ine | e[X]it')

WARNING = Template(
    '# {{line_type}} not valid at {{tiploc}}, press [ENTER] to continue'
)

BUILDER = Template(
    '# Route Builder, START: ```{{tiploc_1}}```, END: ```{{tiploc_2}}```'
)


class LineType(Enum):
    """ Enumeration of line types """
    PATH = 1
    PLATFORM = 2
    LINE = 3


class FullTripTable(Table):
    """ Full trip table """

    HEADERS = [
        "#", "TIPLOC", "Name",
        "Mileage", "Path", "Arrive",
        "Platform", "Depart", "Line",
        "Activity", "Eng. Allowance",
        "Perf. Allowance", "Path. Allowance", "LPB?"
    ]
    STYLE = 'bold cyan'

    def __init__(self):
        """ Init func. """
        super().__init__(
            show_header=True,
            header_style=self.STYLE,
            row_styles=["bold", "reverse"],
            show_lines=True)

        for header in self.HEADERS:
            self.add_column(header)

    def get_lpb(self, tiploc: str) -> str:
        """ Get LPB value for given TIPLOC """

        record = LocationRecord.return_instance(tiploc)
        if not record:
            return None

        lpb = record.force_lpb
        if not lpb:
            return None

        return lpb

    def _add_row(self, items: list):
        """ adds a row """
        self.add_row(*items)

    def populate_table(self, all_items: list):
        """ Populates table """

        for item in all_items:

            self._add_row(item)

    def populate_from_schedule(self, schedule: Schedule) -> None:
        """ Populates a table from a schedule object """
        for row in schedule.rows:
            lpb = self.get_lpb(row.tiploc)
            row.lpb = lpb
            self._add_row(row.__dict__.values())


class RouteRequestTable():
    """ Route Request table """

    def __init__(
            self,
            start: str,
            end: str,
            via: list = None,
            avoid: list = None):

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
    """ Table to display TIPLOC's and related information """
    def __init__(self, results, lines=False):

        self.table = Table(show_header=True, header_style="bold magenta")

        self.table.add_column('#')
        self.table.add_column('TIPLOC')
        self.table.add_column('Name')
        self.table.add_column('STANOX')
        self.table.add_column('Timing Point Type')
        self.table.add_column('Lat/Lon')

        if lines:
            self.table.add_column('Lines')

        for key, match in enumerate(results):
            row_fields = [
                match.location_code,
                match.location_name,
                match.stanox_code,
                match.timing_point_type,
                str(match.wgs_coordinates)
            ]
            if lines and hasattr(match, 'lines'):
                row_fields.append(str(match.lines))

            self.table.add_row(str(key + 1), *row_fields)


class LinkSelectTable():
    """ Table showing valid links """
    def __init__(self, results):
        ""
        self.table = Table(show_header=True, header_style="bold magenta")

        self.table.add_column('#',)
        self.table.add_column('TIPLOC')
        self.table.add_column('Name')

        for row in results:

            self.table.add_row(*row)


class EditSchedule:
    """ Functions to edit a schedule once built """

    @staticmethod
    def build_plt_selection_table(
            options: List[str], 
            cur_plt: str,
            line_type: LineType,
            tiploc: str) -> Table:
        """ Build a table with all valid platforms/lines """

        words = ['into', 'at', 'from']
        col_title = f'{line_type.name} {words[line_type.value - 1]} {tiploc}'

        if len(options) == 1:
            highlight = Style()
        else:
            highlight = Style(underline=True, bold=True)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column('#')
        table.add_column(col_title)
        
        for ref in options:
            if ref[1] == cur_plt:
                table.add_row(*ref, style=highlight)
            else:
                table.add_row(*ref)

        return table

    @staticmethod
    def validate_answer_plt_line(answer: str, options: list) -> bool:
        """ Ensure the answer provided is valid """

        if answer.strip().isnumeric():
            answer = int(answer.strip()) - 1

            if answer <= len(options):
                return True

        return False

    @staticmethod
    def get_link_lines(
            trip: Schedule,
            index: int,
            path=False) -> Union[List, None]:
        """ Get a list containing all NWK valid lines """

        if path and index == 0:
            return None

        if not path and index == len(trip.rows):
            return None

        if path:
            tiploc_1 = trip.rows[index - 1].tiploc
            tiploc_2 = trip.rows[index].tiploc

        else:
            tiploc_1 = trip.rows[index].tiploc
            tiploc_2 = trip.rows[index + 1].tiploc

        return NetworkLink.get_all_lines(tiploc_1, tiploc_2)

    @staticmethod
    def update_lpp(
            trip: Schedule,
            index: int,
            context: Console,
            line_type: LineType) -> None:
        """ Update the platform at the specified tiploc """

        def show_warning() -> None:
            EditSchedule.print_warning(
                    context,
                    Markdown(
                        WARNING.render(
                            line_type=line_type.name,
                            tiploc=tiploc
                        )
                    )
                )

        def update_entry() -> None:
            if line_type == LineType.PATH:
                entry.path = index_options[int(answer)][1]
            if line_type == LineType.PLATFORM:
                entry.platform = index_options[int(answer)][1]
            if line_type == LineType.LINE:
                entry.line = index_options[int(answer)][1]

        entry = trip.rows[index]
        tiploc = entry.tiploc

        cur_val = line_type

        if line_type == LineType.PATH:
            cur_val = entry.path
            if index == 0:
                show_warning()
                return

        if line_type == LineType.PLATFORM:
            cur_val = entry.platform

        if line_type == LineType.LINE:
            cur_val = entry.line
            if index + 1 == len(trip.rows):
                show_warning()
                return

        if line_type == LineType.PLATFORM:
            options = LinePlatform.get_all_lines(tiploc, True)
        else:
            options = EditSchedule.get_link_lines(
                trip,
                index,
                line_type == LineType.PATH)

        if not options:
            options = ['ML']

        index_options = []
        for ind, lnpl in enumerate(options):
            index_options.append([str(ind + 1), lnpl])

        table = EditSchedule.build_plt_selection_table(
            index_options, 
            cur_val,
            line_type,
            tiploc)
        context.print(table)
        answer = context.input()

        if EditSchedule.validate_answer_plt_line(answer, index_options):
            answer = str(int(answer) - 1)
            update_entry()

        trip.extrapolate_lp()

    @staticmethod
    def parse_answer(answer: str) -> List:
        """ Return a list representing the parsed answer """

        if answer.startswith("p"):
            answer = answer[1:]
            return [1, answer]

        if answer.startswith("P"):
            answer = answer[1:]
            return [2, answer]

        if answer.startswith("L"):
            answer = answer[1:]
            return [3, answer]

        if answer.startswith("X"):
            return ['EXIT']

        return [None, None]

    @staticmethod
    def print_warning(context: Console, warning=None) -> None:
        """ Shows a warning, does not process any input """
        if not warning:
            warning = 'Not a valid option, press [ENTER] to try again...'
        Confirm.get_input(prompt=warning, console=context, password=False)

    @staticmethod
    def print_trip(con: Console, current_trip: List, sched: Schedule) -> None:
        """ Print the current trip with edit options """
        con.clear()
        con.print(
            Markdown(
                BUILDER.render(
                    tiploc_1=current_trip[0][2],
                    tiploc_2=current_trip[-1][2])
            )
        )

        tab = FullTripTable()
        sched.update_mileages(None)
        tab.populate_from_schedule(sched)
        con.print(tab)
        answer = CONSOLE.input(EDIT_SCHEDULE)
        answer = EditSchedule.parse_answer(answer)

        if 'EXIT' in answer:
            sys.exit(0)

        if not answer:
            EditSchedule.print_warning(CONSOLE)
            EditSchedule.print_trip(con, current_trip, sched)

        try:
            if answer[1].strip().isnumeric():
                EditSchedule.update_lpp(
                    sched,
                    int(answer[1]),
                    CONSOLE,
                    LineType(answer[0])
                )
                EditSchedule.print_trip(con, current_trip, sched)
        except AttributeError:
            EditSchedule.print_trip(con, current_trip, sched)

psr = argparse.ArgumentParser(
    prog='vstp',
    description='Runs VSTP style path queries',
    epilog='...a work in progress'
)
psr.add_argument('--start', type=str, help='The start TIPLOC')
psr.add_argument('--end', type=str, help='The end TIPLOC')
psr.add_argument(
    '--via',
    type=str,
    help='"TIPLOC, TIPLOC, ..." via location(s)'
)
psr.add_argument(
    '--avoid',
    type=str,
    help='"TIPLOC, TIPLOC, ..." avoid location(s)'
)
psr.add_argument(
    '--legs',
    action='store_true',
    default=False,
    help='Show output as grouped legs between via TIPLOCS'
)
psr.add_argument(
    '--from_loc',
    type=str,
    help='from <TIPLOC> show all linked locations'
)
psr.add_argument('--find', type=str, help='find TIPLOC')
psr.add_argument(
    '--build',
    type=str,
    help='Build a route, provide the first TIPLOC'
)
args = psr.parse_args()

os.system('clear')

if not any(args.__dict__.values()):
    CONSOLE.print(Markdown(NO_ARGS))
    sys.exit()

if args.find:
    CONSOLE.print(Markdown(f"# TIPLOC search: ```{args.find}```"))
    results = LocationRecord.match_locations(args.find)
    table = TiplocTable(results)
    if len(results) > 20:
        with CONSOLE.pager():
            CONSOLE.print(table.table)
    else:
        CONSOLE.print(table.table)
    sys.exit(0)

if args.from_loc:

    CONSOLE.print(Markdown(f"# Network Links: ```{args.from_loc}```"))
    results = f_import.NetworkLink.get_neighbours(args.from_loc, alt=True)
    locs = []
    for result in results:
        rcd = LocationRecord._instances[result]
        rcd.lines = f_import.NetworkLink.get_all_lines(args.from_loc, result)
        locs.append(rcd)
    table = TiplocTable(locs, lines=True)
    CONSOLE.print(table.table)
    sys.exit(0)

if args.build:

    links = []

    def trip_table(cur_trip: list) -> str:
        """ Populate and return a trip table """
        locs = []
        for result in cur_trip:
            rcd = LocationRecord._instances[result[1]]
            locs.append(rcd)
        return TiplocTable(locs).table

    def get_links(tiploc: str) -> str:
        """ Get the NW links for the given tiploc """
        results = f_import.NetworkLink.get_neighbours(tiploc)
        locs = []
        for index, result in enumerate(results):
            rcd = LocationRecord._instances[result]
            locs.append([str(index + 1), rcd.location_code, rcd.location_name])
        return locs

    current_trip = []
    if not LocationRecord.return_instance(args.build):
        CONSOLE.print(Markdown(f"# ERROR, invalid TIPLOC: ```{args.build}```"))
        sys.exit(1)

    # insert the origin point into the current trip
    origin = LocationRecord._instances[args.build]
    current_trip.append(
        [len(current_trip), origin.location_code, origin.location_name]
    )

    while current_trip:
        CONSOLE.clear()

        if len(current_trip) > 1:
            CONSOLE.print(
                Markdown(
                    BUILDER.render(
                        tiploc_1=args.build,
                        tiploc_2=current_trip[-1][1]
                    )
                )
            )

        else:
            CONSOLE.print(
                Markdown(
                    BUILDER.render(
                        tiploc_1=args.build,
                        tiploc_2=args.build
                    )
                )
            )
        CONSOLE.print(Markdown('## Current Route'))
        CONSOLE.print(trip_table(current_trip))
        links = get_links(current_trip[-1][1])
        CONSOLE.print(Markdown('## Next Location Options'))
        print()
        table = LinkSelectTable(links).table
        CONSOLE.print(table)
        print()
        answer = CONSOLE.input(
            Markdown(
                "# [#] Add TIPLOC | [R]emove last entry | [F]ull Schedule | [X]it: "
            )
        )

        if answer == "X":
            CONSOLE.clear()
            if len(current_trip) > 1:
                CONSOLE.print(
                    Markdown(
                        BUILDER.render(
                            tiploc_1=current_trip[0][2],
                            tiploc_2=current_trip[-1][2]
                        )
                    )
                )

            else:
                CONSOLE.print(
                    Markdown(f"# Route Builder, START: ```{args.build}```"))
                CONSOLE.print(Markdown('## Current Route'))
            CONSOLE.print(trip_table(current_trip))
            sys.exit(0)
        if answer == "R" and current_trip:
            if len(current_trip) > 1:
                current_trip.pop()
        if answer.isnumeric():
            answer = int(answer) - 1

            try:
                next_loc = LocationRecord._instances[links[answer][1]]
                current_trip.append(
                    [
                        len(current_trip),
                        next_loc.location_code,
                        next_loc.location_name
                    ]
                )
            except IndexError:
                continue

        if answer == "F" and len(current_trip) > 1:
            EditSchedule.print_trip(
                CONSOLE,
                current_trip,
                Schedule.factory(current_trip)
            )

            sys.exit()

    sys.exit(0)

via = []
avoid = []

if args.via:
    via = [tpl.strip() for tpl in args.via.split(',')]

if args.avoid:
    avoid = [tpl.strip() for tpl in args.avoid.split(',')]

CONSOLE.print(Markdown("# VSTP query"))
CONSOLE.print(
    RouteRequestTable(args.start, args.end, args.via, args.avoid).grid
)

path = Pathfinder(args.start, args.end, legs=args.legs, via=via, avoid=avoid)
path.search(std_out=False)

CONSOLE.print(Markdown("# Results"))

trip = []

for index, tiploc in enumerate(path.route_locations):

    loc_name = LocationRecord.return_instance(tiploc).location_name
    trip.append([index, tiploc, loc_name])

EditSchedule.print_trip(
    CONSOLE,
    trip,
    Schedule.factory(trip)
)
