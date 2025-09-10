#!/bin/env dls-python

import sys

from motorhome import *

# find the plc number, component name and filename
num, name, filename = parse_args()

# set some defaults
plc = PLC(int(num), timeout=900000, post=None, ctype=PMAC)

# KB Mirror
if name == "GEO4":
    plc = PLC(int(num), timeout=900000, post=None, ctype=GEOBRICK)
    plc.add_motor(2, group=2, htype=RLIM, post=14841)  # KB mirror 1 VFM tilt
    plc.add_motor(3, group=3, htype=RLIM, post=15479)  # KB mirror 2 HFM tilt
    plc.add_motor(4, group=4, htype=RLIM, post=-844155.5)  # Pinhole vertical
    plc.add_motor(5, group=5, htype=RLIM, post=844155.5)  # Pinhole horizontal
    plc.add_motor(6, group=6, htype=RLIM, post=-844155.5)  # Wires horizontal
    plc.add_motor(7, group=7, htype=RLIM, post=-844155.5)  # Wires vertical
    plc.add_motor(8, group=8, htype=HSW, jdist=20000)  # Aerotech tilt

else:
    sys.stderr.write("***Error: Can't make homing PLC %d for %s\n" % (num, name))
    sys.exit(1)

# write out the plc
plc.write(filename)
