# VSTP
## UK Rail route finder

### What is it?
It is a collection of python modules that together calculate a route from TIPLOC to TIPLOC, using BPLAN data.

## Whats in a name - VSTP?
This repo represents early efforts to create a system that can eventually be used to create ad-hoc train schedules; i.e. those that are not published within the working timetable or its incremental updates and without reference to an existing schedule or service template. The rail industry refers to the creation of such schedules as VSTP - *Very Short Term Planning*; hence the name for the repo is VSTP.

## How does it work?
In its current form, and at its heart, is an algorythm which searches for the shortest path between 2 points; A* [A star]. A* is an enhancement to another well known searching algorythm, Dykstra's algorythm, by adding an additional measure, or heuristic, for distance. The application does however modify things slightly to take into account some of the limitations and oddities of railway geography; more will be explained later!

## How do I use it?
Follow the instructions below!

### Requirements
* Python 3 (we used 3.8.10)
* Aside from packages provided in the standard library, for your convenience, we supply a *requirements.txt* file for 3rd party libraries used within this application
  * Note: We strongly recommend using a virtual environment (venv) when running/playing with this application: https://docs.python.org/3/library/venv.html
* A copy of the Network Rail BPLAN document; this contains, amongst lots of reference data, a representation of UK rail geographical data.
  * https://wiki.openraildata.com/index.php?title=BPLAN_data_structure describes the format and content
  * The file can be downloaded here: https://wiki.openraildata.com/index.php?title=BPLAN_Geography_Data

### BPLAN processing
Before using the application, we need to split up the BPLAN into separate parts; this makes processing what is a massive document a little easier.

* Location Records (LOC):
  ```bash
  $ grep ^LOC <bplan file> > LOC
  ```
* Network Links (NWK):
  ```bash
  $ grep ^NWK <bplan file> > NWK
  ```

You should now have 2 files in the root directory, LOC and NWK - these are both needed by the application.

### Unit & Integration Tests
It is advisable to run the included tests before using the application, thus:
* Navigate to the application root folder,
* at the prompt, to run both Unit and Integration tests:
  ```python
  $ pytest -vv -s -x tests/*
  ```
* at the prompt, to run only unit tests:
  ```python
  $ pytest -vv -s -x tests/unit_tests/*
  ```
* Likewise, for Integration tests only:
  ```python
  $ pytest -vv -s -x tests/integration_tests/*
  ```
The Integration tests in particular will provide useful information should the application not operate as desired.

### Searching for a route - getting started
Not forgetting that this application is at a very early stage of development, the easiest way to search for a route between two TIPLOCs is as follows:

* Within the ```main()``` function of ```main.py```, you will note an example in docstring.

    * Instantiate a ```Pathfinder``` object with the following parameters:
        * ```Pathfinder(FROM, TO)``` where FROM and TO represent the start and end TIPLOCs
        * Optionally, users can specify ```via=[TIPLOC, TIPLOC, TIPLOC]``` keyword argument; this forces the routing path to use these TIPLOCs
        * Optinally, users can specify ```avoid=[TIPLOC, TIPLOC]``` keyword argument; this ensures the routing avoids these TIPLOCs

        * In summary, a full example would therefore be:
            ```
            PATH = Pathfinder('CREWE', 'DRBY', via=['KIDSGRV', 'ALSAGER'], avoid=['STAFFRD'])
            ```
    * To start the search, make a call to ```PATH.search()``` The route is printed to STDOUT.

### Limitations and Caveats
During its development, we have noticed that the BPLAN data is not as accurate as one would assume and this affects the routing of services to some extent.

For example, for a route from CREWE to WEAVERJ, the routing application will not find a direct route; this is because there is an error in the Network Links BPLAN data - in particular the arrival and departure direction are incorrect. This can be resolved by tactical use of the via directive.

### Next Steps
We are in the process of adding issues into the repo to indicate further enhancement needs and efforts but initially they will be:
* Input (or default) service timing load/traction type
* Extrapolate timings based on timing load/traction type
