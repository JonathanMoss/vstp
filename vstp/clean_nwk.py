import os
from sqlmodel import Session, create_engine, select, and_
from models import network_link as NWK
from models import timing_link as TLK

DB_CON_STRING = os.getenv("DB_CON_STRING", 'sqlite:///vstp.db')
engine = create_engine(DB_CON_STRING, echo=False)

def get_network_links() -> list:
    with Session(engine) as session:
        stmt = select(NWK.NetworkLink)
        return session.execute(stmt).fetchall()
    
def get_timing_link(origin: str, destination: str) -> TLK.TimingLink:
    with Session(engine) as session:
        stmt = select(
            TLK.TimingLink
        ).filter(
            and_(
                TLK.TimingLink.origin == origin,
                TLK.TimingLink.destination == destination,

            )
        )
        
                # TLK.TimingLink.speed == '60',
                # TLK.TimingLink.entry_speed == '-1',
                # TLK.TimingLink.exit_speed == '-1'

        results = [result[0] for result in session.execute(stmt)]
        if not results:
            print(f'NO RESULTS: {origin}, {destination}')
            return None
        return sorted(results, key=lambda result: result.running_time)[0]
    

def main():
    for nwk in get_network_links():
        # print(nwk)
        origin = nwk[0].origin
        destination = nwk[0].destination
        result = get_timing_link(origin, destination)
        print(nwk[0].distance)
        if not result:
            exit()
            continue
        
        miles_per_second = int(result.speed) / 3600
        distance_miles = miles_per_second * result.running_time
        distance_metres = distance_miles * 1609.34

        print(miles_per_second)
        print(distance_miles)
        print(int(distance_metres))
        print()
        
        

if __name__ == "__main__":
    main()
