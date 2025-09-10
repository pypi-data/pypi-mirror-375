#!/usr/bin/env dls-python

# Import the motorhome PLC generation library
from motorhome import *

# find the plc number, component name and filename
num, name, filename = parse_args()

# set some defaults
# "i":post home move to move back to initial position
post = "i"

# configure the axes according to name

# BRICK19

# There is no homing routine for the Tomo SAXS stages
# STEP-19 axis 5 & 6
# as they are rotation stages, which should be homed either
# forward or backward depending on its position.
# This can be done from the 'more' screen for the motor.
# This is because the cables for the altitude stage mean
# the azimuth stage can't rotate 360 to home.

if name == "STABL":  # Sample Table, BASE in synoptic
    plc = PLC(num, htype=HSW, ctype=GEOBRICK)
    plc.add_motor(1, jdist=-1000, group=2)
    plc.add_motor(2, jdist=-1000, group=3)
    plc.add_motor(3, jdist=-1000, group=4)
elif name == "PXY2":
    plc = PLC(num, ctype=GEOBRICK, post=post)
    plc.add_motor(7, group=2, htype=RLIM, jdist=-1000)
    plc.add_motor(8, group=3, htype=RLIM, jdist=-1000)
elif name == "SPY":  # SAXS Platform Table Y
    plc = PLC(num, htype=HSW, ctype=GEOBRICK, post=post)
    plc.add_motor(17, jdist=-1000, group=2, ms=5)
else:
    sys.stderr.write("***Error: Can't make homing PLC %d for %s\n" % (num, name))
    sys.exit(1)

# write out the plc
plc.write(filename)
