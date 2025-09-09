#!/usr/bin/env dls-python

# Import the motorhome PLC generation library
from motorhome import *

# find the plc number, component name and filename
num, name, filename = parse_args()

# set some defaults
# "i":post home move to move back to initial position
post = "i"

# -------PMAC2-------

if name == "S3":
    plc = PLC(
        num, htype=LIMIT, ctype=PMAC, post=post
    )  # all axes home off limit switches
    for axis in [3, 4]:  # group 2 is Y:PLUS, Y:MINUS
        plc.add_motor(axis, group=2)
    for axis in [1, 2]:  # group 3 is X:PLUS, X:MINUS
        plc.add_motor(axis, group=3)
elif name == "D4":
    plc = PLC(
        num, htype=LIMIT, ctype=PMAC, post=post
    )  # axis homes off home switch close to HLIM
    plc.add_motor(5)
elif name == "D5":
    plc = PLC(
        num, htype=LIMIT, ctype=PMAC, post=post
    )  # axis homes off home switch close to HLIM
    plc.add_motor(6)
elif name == "D6":
    plc = PLC(
        num, htype=RLIM, ctype=PMAC, post=post
    )  # axis homes off home switch close to HLIM
    plc.add_motor(7, enc_axes=[8])
else:
    sys.stderr.write("***Error: Can't make homing PLC %d for %s\n" % (num, name))
    sys.exit(1)

# write out the plc
plc.write(filename)
