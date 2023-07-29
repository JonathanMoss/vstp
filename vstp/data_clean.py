import os
import sys
import subprocess
import json
from functools import lru_cache
from time import sleep
from typing import Union
from sqlmodel import Session, create_engine, select, or_, cast, Numeric
sys.path.insert(0, './vstp/models')
from models import location as LOC
from models import network_link as NWK

DB_CON_STRING = os.getenv("DB_CON_STRING", 'sqlite:///vstp.db')
engine = create_engine(DB_CON_STRING, echo=False)

def remove_bus(table: str, session: Session) -> dict():
    """Remove references to BUS trips in the provided table"""
    
    LINE = 'line'
    if table == 'timinglink':
        LINE = 'line_code'
    
    def total() -> int:
        """Get table totals"""
        return session.execute(
            f'SELECT COUNT(*) FROM {table};'
        ).fetchone()[0]
    
    # Get total records
    before_total = total()
    
    # Delete all BUS records
    stmt = f"""
    DELETE
    FROM {table}
    WHERE {LINE} LIKE "%BUS%";""".strip()
    session.execute(stmt)
    
    # Get total records
    after_total = total()
    deleted = before_total - after_total
    
    print(f'Delete BUS: {table}')
    print(f'\tBefore: {before_total}, Deleted: {deleted}, After: {after_total}')

def update_bad_distance() -> None:
    """Update NWK records with questionable distances"""
    
    def load_json(stdout: Union[str, bytes]) -> Union[None, str]:
        """Loads a json object from a geocoder request"""
        if isinstance(stdout, bytes):
            stdout = stdout.decode('utf-8')
        try:
            return json.loads(stdout)
        except Exception:
            return None
    
    @lru_cache(maxsize=1000)   
    def geo_info(wgs_coords: tuple) -> Union[dict, None]:
        """Sends a geocoder request and returns the results as dict"""
        args = f'"{wgs_coords[0]}, {wgs_coords[1]}"'
        proc = subprocess.run(
            ['geocode', '-m', 'reverse', '-p', 'osm',
            args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        return load_json(proc.stdout)
    
    @lru_cache(maxsize=1000)
    def get_loc(tiploc: str, session: Session) -> LOC.Location:
        """Returns the location record specified in the TIPLOC"""
        location = select(
            LOC.Location
        ).where(
            LOC.Location.tiploc == tiploc
        )
        return session.execute(location).fetchone()[0]

    
    with Session(engine) as session:
        
        # Remove the BUS trips from timinglink
        remove_bus('timinglink', session)
        
        # Remove the BUS trips from networklink
        remove_bus('networklink', session)
        session.commit()
        
        # Define query to fetch all network link records where
        # distance is less that 100 metres.
        stmt = select(
            NWK.NetworkLink
        ).where(
            or_(
                NWK.NetworkLink.distance == None, 
                cast(NWK.NetworkLink.distance, Numeric) < 100
            )
        )
        
        # Loop through the query results
        for row in [record[0] for record in session.execute(stmt)]:

            # Fetch the location record
            origin_loc = get_loc(row.origin, session)
            
            # Check if the easting/northing coordinates are valid
            if not origin_loc.are_coords_valid:
                continue
            
            # Fetch the destination record
            dest_loc = get_loc(row.destination, session)
            
            # Check if the easting/northing coordinates are valid
            if not dest_loc.are_coords_valid:
                continue
            
            # Check if wgs coordinates are available
            if not all([origin_loc.wgs_coordinates, dest_loc.wgs_coordinates]):
                continue
            
            # Calculate the new distance
            distance = LOC.Location.distance(
                origin_loc.wgs_coordinates,
                dest_loc.wgs_coordinates,
                miles=False
            )
            
            # If we could not calculate the distance, move on
            if not distance:
                continue
            
            if distance > 99999:
                distance = str(int(distance)).rjust(5,'0')
                print(f'{origin_loc.tiploc} -> {dest_loc.tiploc} was {row.distance}, is now {distance}')
                print(origin_loc)
                print(origin_loc.wgs_coordinates)
                info = geo_info(origin_loc.wgs_coordinates)
                if not info:
                    continue
                if 'postal' not in info:
                    print(info)
                else:
                    print(info["postal"])
                sleep(0.5)
                print(dest_loc)
                print(dest_loc.wgs_coordinates)
                info = geo_info(dest_loc.wgs_coordinates)
                if not info:
                    continue
                if 'postal' not in info:
                    print(info)
                else:
                    print(info["postal"])
                sleep(0.5)
                print('*' * 20)
        
    


    # # Removes BUS values from Network Links
    # NWK_BUS = """
    # DELETE 
    # FROM networklink
    # WHERE line LIKE "%BUS%";
    # """.strip()
    # session.execute(NWK_BUS)

    # # Removes BUS values from Timing Links
    # TLK_BUS = """
    # DELETE 
    # FROM timinglink
    # WHERE line_code LIKE "%BUS%";
    # """.strip()
    # session.execute(TLK_BUS)

    # NWK_PAIRS = """
    # SELECT DISTINCT(origin || ',' || destination)
    # FROM networklink;
    # """.strip()
    # nwk_pairs = [result[0] for result in session.execute(NWK_PAIRS)]
    
    # TLK_PAIRS = """
    # SELECT DISTINCT(origin || ',' || destination)
    # FROM timinglink;
    # """.strip()
    # tlk_pairs = [result[0] for result in session.execute(TLK_PAIRS)]
    
    
    
      
    #     northing, easting = session.execute(f'SELECT northing, easting FROM location WHERE tiploc = "{result.origin}";').fetchone()
    #     print(f'Origin: {result.origin} [{northing}, {easting}]')
    #     northing, easting = session.execute(f'SELECT northing, easting FROM location WHERE tiploc = "{result.destination}";').fetchone()
    #     print(f'Destination: {result.destination} [{northing}, {easting}]')
    #     print(result.distance)
    #     print('*' *20)

    # statement = select(LOC.Location)
    # results = session.exec(statement).fetchall()
    
    # for result in results:
    #     wgs_coordinates = result.wgs_coordinates
    #     if not wgs_coordinates:
    #         continue
    #     print(result.name, result.are_coords_valid)
    # session.commit()
    # exit()
  
  
# missing_from_tlk = 0
# print('IN NWK, MISSING FROM TLK:')
# for nwk in nwk_pairs:
#     if nwk not in tlk_pairs:
#         missing_from_tlk += 1
#         print(missing_from_tlk, nwk)
        
# missing_from_nwk = 0
# print('IN TLK, MISSING FROM NWK:')
# for tlk in tlk_pairs:
#     if tlk not in nwk_pairs:
#         missing_from_nwk += 1
#         print(missing_from_nwk, tlk)

def main() -> None:
    update_bad_distance()
        
if __name__ == '__main__':
    main()
