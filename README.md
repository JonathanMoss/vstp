# VSTP
## UK Rail route finder

### What is it?
It is a collection of python modules that together calculate a route from TIPLOC to TIPLOC, using BPLAN data.

## Whats in a name - VSTP?
This repo represents early efforts to create a system that can eventually be used to create ad-hoc train schedules; i.e. those that are not published within the working timetable or its incremental updates. The rail industry refers to the creation of such schedules as VSTP - *Very Short Term Planning*; hence the name for the repo is VSTP.

### How do I use it?
Follow the instructions below!

### Requirements
* Python 3 (we used 3.8.10)
* Aside from packages provided in the standard library, for your convenience, we supply a requirements.txt file for 3rd party libraries used within this application
* A copy of the Network Rail BPLAN document; this contains, amongst lots of reference data, a representation of UK rail geographical data.
  * https://wiki.openraildata.com/index.php?title=BPLAN_data_structure describes the format and content
  * The file can be downloaded here: https://wiki.openraildata.com/index.php?title=BPLAN_Geography_Data

