### Simple search, without via or avoid ###

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
