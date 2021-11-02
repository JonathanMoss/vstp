### Setup

The application requires the following extracts from the BPLAN data file:

* ```NWK``` Containing network link records
* ```LOC``` Containing BPLAN location records

The files should be places in the directory from where the application is called, for example:

```
root  
│
└───vstp
│		conftest.py
│		err.py
│		location_record.py
│		main.py.py
│		network_links.py
│		pathfinder.py
NWK
LOC
```
Extract the necessary records from the BPLAN as follows:

```bash
$ grep ^LOC <bplan file> > LOC
```

```bash
$ grep ^NWK <bplan file> > NWK
```

### Running the application - minimal example

```python
from vstp.pathfinder import Pathfinder
import vstp.bplan_import as f_import

# import the NWK and LOC files - needed only once
f_import.import_location()
f_import.import_network_links()

# Define the path criteria
PATH=Pathfinder('CREWE', 'DRBY')
PATH.search()  # Start the search and output to STDOUT

PATH=Pathfinder('DRBY', 'CREWE')
PATH.search()
```
### Simple search, without via or avoid

```python
path = Pathfinder('CREWE', 'DRBY')
path.search()
```
This searches for the shortest route from Crewe Station to Derby Station and the output is:

```bash
CREWE
CREWSJN
BTHLYJN
ALSAGER
KIDSGRV
STOKEOT
STOKOTJ
LNTN
CAVRSWL
UTOXSB
TUTBURY
NSJDRBY
STSNJN
DRBYLNW
DRBY
```

### Search for a route with one or more via TIPLOCs specified

```python
path = Pathfinder('CREWE', 'DRBY', via=['STAFFRD'])
path.search()
```
Vias are expressed as a list of strings, thus: ```['TIPLOC', 'TIPLOC']```

This searches for the shortest route from Crewe Station to Derby Station via Stafford Station, the output is:

```bash
CREWE
CREWBHJ
MADELEY
LBRDFJN
STAFFRD
	STAFFRD
	COLWICH
	RUGLYNJ
	RUGL
	RUGLBJN
	HDNS
	CNCKMGF
	BLOXWCH
	WALSRJN
	PLNEJT
	WTRORWJ
	WTRORTN
	KNGSBYJ
	TMWTHHL
	WICHNRJ
	BURTNOT
	CLMLJN
	NSJDRBY
	STSNJN
	DRBYLNW
	DRBY
```

### Search for a route with one or more avoid TIPLOCs specified

```python
path = Pathfinder('CREWE', 'DRBY', avoid=['ALSAGER'])
path.search()
```
Avoids are expressed as a list of strings, thus: ```['TIPLOC', 'TIPLOC']```

This searches for the shortest route from Crewe Station to Derby Station and expresses that Alsager should be avoided; the output is:

```bash
CREWE
CREWBHJ
MADELEY
LBRDFJN
STAFFRD
COLWICH
RUGLYNJ
RUGL
RUGLBJN
HDNS
CNCKMGF
BLOXWCH
WALSRJN
PLNEJT
WTRORWJ
WTRORTN
KNGSBYJ
TMWTHHL
WICHNRJ
BURTNOT
CLMLJN
NSJDRBY
STSNJN
DRBYLNW
DRBY
```
