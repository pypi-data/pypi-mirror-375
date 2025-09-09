#!/usr/bin/env dls-python

# Import the motorhome PLC generation library
from motorhome import *

# find the plc number, component name and filename
num, name, filename = parse_args()

# set some defaults
# "i":post home move to move back to initial position
post = "i"

# --------PMAC1------

if name == "S1":
    plc = PLC(
        num, htype=LIMIT, ctype=PMAC, post=post
    )  # all axes home off limit switches
    # group 2 is Y:PLUS, Y:MINUS
    plc.add_motor(1, group=2)
    plc.add_motor(3, group=2)
    # group 3 is X:PLUS, X:MINUS
    plc.add_motor(2, group=3)
    plc.add_motor(4, group=3)
elif name == "D1":
    plc = PLC(
        num, htype=HSW_HLIM, ctype=PMAC, post=post
    )  # axis homes off home switch close to HLIM
    plc.add_motor(5, jdist=-2000)
elif name == "D2":
    plc = PLC(
        num, htype=HSW_HLIM, ctype=PMAC, post=post
    )  # axis homes off home switch close to HLIM
    plc.add_motor(6, jdist=-2000)
elif name == "S2":
    plc = PLC(
        num, htype=LIMIT, ctype=PMAC, post=post
    )  # all axes home off limit switches
    for axis in [14, 15]:  # group 2 is Y:PLUS, Y:MINUS
        plc.add_motor(axis, group=2)
    for axis in [12, 13]:  # group 3 is X:PLUS, X:MINUS
        plc.add_motor(axis, group=3)
elif name == "D3":
    plc = PLC(
        num, htype=LIMIT, ctype=PMAC, post=post
    )  # axis homes off home switch close to HLIM
    plc.add_motor(16)
elif name == "VFM":
    plc = PLC(num, htype=LIMIT, ctype=PMAC, post=post)  # axis homes off limit switch
    for axis in [17, 18, 19]:  # group 2 is :Y1,:Y2,:Y3
        plc.add_motor(axis, group=2)
    plc.configure_group(group=2, pre="i1722=10 i1822=10 i1922=10")
    # group 3 is :X1,:X2
    plc.add_motor(20, group=3)
    plc.add_motor(21, group=3)
    plc.configure_group(group=3, pre="i2022=4 i2122=4")
elif name == "HFM":
    plc = PLC(num, htype=LIMIT, ctype=PMAC, post=post)  # axis homes off limit switch
    for axis in [24, 25, 26]:  # group 2 is :Y1,:Y2,:Y3
        plc.add_motor(axis, group=2)
    plc.configure_group(group=2, pre="i2422=10 i2522=10 i2622=10")
    # group 3 is :X1,:X2
    plc.add_motor(27, group=3)
    plc.add_motor(28, group=3)
    plc.configure_group(group=3, pre="i2722=4 i2822=4")

else:
    sys.stderr.write("***Error: Can't make homing PLC %d for %s\n" % (num, name))
    sys.exit(1)

# write out the plc
plc.write(filename)
