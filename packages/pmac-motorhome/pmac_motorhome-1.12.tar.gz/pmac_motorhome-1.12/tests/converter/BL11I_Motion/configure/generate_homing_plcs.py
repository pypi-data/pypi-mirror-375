#!/bin/env dls-python

# Import the motorhome PLC generation library
from motorhome import *

# find the plc number, component name and filename
num, name, filename = parse_args()

# set some defaults
plc = PLC(num, post="i", ctype=PMAC)

######################### PMAC3 ################################################
if name == "S1":
    # all axes home off reference marks
    for axis in [3, 2]:  # group 2 is XA, YB
        plc.add_motor(axis, htype=HSW, jdist=1000, group=2)
    for axis in [1, 4]:  # group 3 is YA, XB
        plc.add_motor(axis, htype=HSW, jdist=1000, group=3)
elif name == "D1":
    # axis homes off home switch close to HLIM
    plc.add_motor(27, htype=HSW_HLIM)
elif name == "DCM":
    plc.add_motor(2, group=2, htype=HSW, jdist=5000)  # Bragg homes off a reference mark
    plc.add_motor(
        1, group=3, htype=RLIM
    )  # Everything else homes on release of the limit
    plc.add_motor(3, group=4, htype=RLIM)
    plc.add_motor(5, group=5, htype=RLIM)
    plc.add_motor(6, group=6, htype=RLIM)
elif name == "S2":
    # all axes home off reference marks close to HLIM
    for axis in [11, 9]:  # group 2 is X+, Y+
        plc.add_motor(axis, htype=HSW_HLIM, jdist=-1000, group=2)
    # group 3 is X-, Y-
    plc.add_motor(12, htype=HSW_HLIM, jdist=-1000, group=3)
    plc.add_motor(10, htype=RLIM, group=3)
elif name == "BPM1":
    # axis homes off limit switch
    plc.add_motor(5, htype=LIMIT)
elif name == "M1":
    for axis in [23, 24]:  # X jacks home on a limit
        plc.add_motor(axis, group=2, htype=LIMIT)
    for axis in [25, 26]:  # Y jacks home on a reference mark
        plc.add_motor(axis, group=2, jdist=-1000, htype=HSW)
    plc.add_motor(20, group=3, htype=LIMIT)  # Bender homes on a limit switch
    for axis in [21, 22]:  # Pitch, Roll home on a home switch
        plc.add_motor(axis, group=4, htype=HSW)
elif name == "S3":
    # all axes home off reference marks close to HLIM
    for axis in [15, 13]:  # group 2 is X+, Y+
        plc.add_motor(axis, htype=HSW_HLIM, jdist=-1000, group=2)
    for axis in [16, 14]:  # group 3 is X-, Y-
        plc.add_motor(axis, htype=HSW_HLIM, jdist=-1000, group=3)
elif name == "BPM2":
    # axis homes off limit switch
    plc.add_motor(7, htype=LIMIT)


else:
    sys.stderr.write("***Error: Can't make homing PLC %d for %s\n" % (num, name))
    sys.exit(1)

# write out the plc
plc.write(filename)
