#!/bin/env dls-python

import sys

from motorhome import *

# find the plc number, component name and filename
num, name, filename = parse_args()

# set some defaults
plc = PLC(int(num), timeout=900000, post=None, ctype=GEOBRICK)

# configure the axes according to name
if name == "FESLIT01":
    plc.add_motor(1, htype=LIMIT, group=2)  # YPLUS
    plc.add_motor(2, htype=LIMIT, group=3)  # YMINUS
    plc.add_motor(3, htype=LIMIT, group=4)  # XPLUS
    plc.add_motor(4, htype=LIMIT, group=5)  # XMINUS

elif name == "SLIT01":
    plc.add_motor(8, htype=HSW, group=2, jdist=-4000)  # YPLUS
    plc.add_motor(6, htype=HSW, group=3, jdist=-4000)  # YMINUS
    plc.add_motor(5, htype=HSW, group=4, jdist=-4000)  # XPLUS
    plc.add_motor(7, htype=HSW, group=5, jdist=-4000)  # YMINUS

elif name == "FILTER01":
    plc.add_motor(3, htype=HSW_HLIM, group=2)  # F1
    plc.add_motor(4, htype=HSW_HLIM, group=3)  # F2
    plc.add_motor(5, htype=HSW_HLIM, group=4)  # F3
    plc.add_motor(6, htype=HSW_HLIM, group=5)  # F4
    plc.add_motor(7, htype=HSW_HLIM, group=6)  # F5
    plc.add_motor(8, htype=HSW_HLIM, group=7)  # F6

elif name == "MIRROR01":
    plc.add_motor(1, htype=HSW_HLIM, group=2, jdist=-2000)  # PITCHCOARSE
    plc.add_motor(3, htype=HSW, group=3, jdist=-2000)  # X
    plc.add_motor(4, htype=HSW, group=4, jdist=-2000)  # Y
    plc.add_motor(2, htype=HSW, group=5)  # CURVATURE

elif name == "DIAGNOSTIC01":
    plc.add_motor(1, htype=HSW_HLIM, group=2)  # X

elif name == "DIAGNOSTIC02":
    plc.add_motor(2, htype=HSW_HLIM, group=2)  # X

elif name == "DIAGNOSTIC04":
    plc.add_motor(1, htype=HSW_HLIM, group=2)  # X

elif name == "SLIT02":
    plc.add_motor(7, htype=LIMIT, group=2)  # YPLUS
    plc.add_motor(8, htype=LIMIT, group=3)  # YMINUS
    plc.add_motor(5, htype=LIMIT, group=4)  # XPLUS
    plc.add_motor(6, htype=LIMIT, group=5)  # XMINUS

elif name == "SLIT03":
    plc.add_motor(3, htype=LIMIT, group=2)  # YPLUS
    plc.add_motor(4, htype=LIMIT, group=3)  # YMINUS
    plc.add_motor(2, htype=LIMIT, group=4)  # XPLUS
    plc.add_motor(1, htype=LIMIT, group=5)  # XMINUS

elif name == "DCM01":
    plc.add_motor(7, htype=RLIM, group=2, jdist=-1000)  # BRAGG
    plc.add_motor(4, htype=RLIM, group=3, jdist=1000)  # ROLL
    plc.add_motor(
        5, htype=RLIM, group=4, jdist=1000
    )  # Z; reads encoder on #13 so zero this after home
    plc.configure_group(4, post='cmd "#13hmz"')  # ...so zero this after home
    plc.add_motor(6, htype=RLIM, group=5, jdist=1000)  # Y
    plc.add_motor(8, htype=RLIM, group=6, jdist=1000)  # PITCH
    plc.add_motor(1, htype=RLIM, group=7, jdist=1000, post="z-2486955")  # JACK1
    plc.add_motor(2, htype=RLIM, group=7, jdist=1000, post="z-2538611")  # JACK2
    plc.add_motor(3, htype=RLIM, group=7, jdist=1000, post="z-2512984")  # JACK3

elif name == "DIAGNOSTIC05":
    plc.add_motor(8, htype=HSW_HLIM, group=2)  # Y

elif name == "SLIT04":
    plc.add_motor(1, htype=RLIM, group=2)  # XMINUS
    plc.add_motor(2, htype=RLIM, group=3)  # XPLUS
    plc.add_motor(3, htype=RLIM, group=4)  # YMINUS
    plc.add_motor(4, htype=RLIM, group=5)  # YPLUS

elif name == "SLIT05":
    plc.add_motor(8, htype=RLIM, group=2)  # XMINUS
    plc.add_motor(7, htype=RLIM, group=3)  # XPLUS
    plc.add_motor(5, htype=RLIM, group=4)  # YMINUS
    plc.add_motor(6, htype=RLIM, group=5)  # YPLUS

elif name == "ZONEPLATE01":
    plc.add_motor(1, htype=LIMIT, group=2)  # X
    plc.add_motor(2, htype=LIMIT, group=3)  # Y
    plc.add_motor(3, htype=LIMIT, group=4)  # Z

elif name == "STAGE02":
    plc.add_motor(3, htype=HSW, group=2, jdist=1000)  # X
    plc.add_motor(4, htype=HSW, group=3, jdist=-4444)  # Y
    plc.add_motor(5, htype=HSW, group=4, jdist=-1000)  # Z

elif name == "DIFF01":
    plc.add_motor(1, htype=LIMIT, group=2)  # DX
    plc.add_motor(2, htype=LIMIT, group=3)  # DY
    plc.add_motor(3, htype=LIMIT, group=4)  # DZ
    plc.add_motor(4, htype=LIMIT, group=5)  # OMEGA
    plc.add_motor(5, htype=LIMIT, group=6)  # ALPHA
    plc.add_motor(6, htype=LIMIT, group=7)  # THETA

elif name == "SCOPE01":
    plc.add_motor(1, htype=LIMIT, group=2)  # X
    plc.add_motor(2, htype=LIMIT, group=3)  # Y
    plc.add_motor(3, htype=LIMIT, group=4)  # FOCUS
    plc.add_motor(4, htype=LIMIT, group=5)  # LASER

elif name == "TABLE01":
    plc.add_motor(1, htype=HSW, group=2, jdist=-4000)
    plc.add_motor(2, htype=HSW, group=2, jdist=-4000)
    plc.add_motor(3, htype=HSW, group=2, jdist=-4000)
    plc.add_motor(4, htype=HSW, group=2, jdist=-4000)

elif name == "STAGE01":
    plc.add_motor(1, htype=RLIM, group=2)  # Y axis
    plc.add_motor(2, htype=HSW, group=3, jdist=-2000)  # Z axis
    plc.add_motor(3, htype=HSW, group=4, jdist=-2000)  # X axis
    plc.add_motor(6, htype=HSW, group=5, jdist=-1000)  # Rotary air bearing
    plc.add_motor(4, htype=HSW, group=6, jdist=-1000)  # Pitch
    plc.add_motor(5, htype=HSW, group=7, jdist=-1000)  # Roll

elif name == "TRANS01":
    plc.add_motor(7, htype=RLIM, group=2)  # Translation

elif name == "TABLE99":
    plc.add_motor(1, htype=LIMIT, group=2)  # X
    plc.add_motor(2, htype=LIMIT, group=3)  # Y

else:
    sys.stderr.write("***Error: Can't make homing PLC %d for %s\n" % (num, name))
    sys.exit(1)

# write out the plc
plc.write(filename)
