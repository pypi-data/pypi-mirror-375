#!/bin/env dls-python

# Import the motorhome PLC generation library
from motorhome import *

# find the plc number, component name and filename
num, name, filename = parse_args()

# set some defaults
plc = PLC(num, post="i", ctype=BRICK)

# -------PMAC 1---------
if name == "S1":
    # Home off reference marks and return to initial position
    plc = PLC(num, htype=HSW, post="i", jdist=-400, ctype=1)
    for axis in [1, 2]:  # group 2 is X1, X2
        plc.add_motor(axis, group=2)
    for axis in [3, 4]:  # group 3 is Y1, Y2
        plc.add_motor(axis, group=3)
    plc.write(filename)

elif name == "A1":
    # Home on home switch at top of travel (just under positive limit).
    plc = PLC(num, htype=HOME, post=None, ctype=1)
    plc.add_motor(8, group=2)
    plc.write(filename)

elif name == "M1":
    # For the jacks, home off reference marks and return to initial position (there is also a home offset set in PMAC).
    plc = PLC(num, htype=HSW, post="i", jdist=-1000, ctype=1)
    for axis in [6, 7]:  # group 2 is Jacks
        plc.add_motor(axis, group=2)
    # group 3 is Bend (home on neg limit, and there is a nominal position in home offset on PMAC)
    plc.add_motor(5, group=3, htype=LIMIT)
    plc.write(filename)

# -------PMAC 2---------
elif name == "S2":
    # Home off reference marks and return to initial position
    plc = PLC(num, htype=HSW_HLIM, post="i", jdist=400, ctype=1)
    for axis in [1, 2]:  # group 2 is X1, X2
        plc.add_motor(axis, group=2)
    for axis in [3, 4]:  # group 3 is Y1, Y2
        plc.add_motor(axis, group=3)
    plc.write(filename)

elif name == "S3":
    # Home off reference marks and return to initial position
    plc = PLC(num, htype=HSW, post="i", jdist=-400, ctype=1)
    for axis in [5, 6]:  # group 2 is X1, X2
        plc.add_motor(axis, group=2)
    for axis in [7, 8]:  # group 3 is Y1, Y2
        plc.add_motor(axis, group=3)
    plc.write(filename)

# -------PMAC 3---------
elif name == "A2":
    # Home on home switch at top of travel (just under positive limit).
    plc = PLC(num, htype=HOME, post=None, ctype=1)
    plc.add_motor(1, group=2)
    plc.write(filename)

elif name == "M2":
    # For the jacks, home off reference marks and return to initial position (there is also a home offset set in PMAC).
    plc = PLC(num, htype=HSW, post="i", jdist=-1000, ctype=1)
    # group 2 is Bend (home on neg limit. No nominal position).
    plc.add_motor(2, group=2, htype=LIMIT)
    for axis in [3, 4]:  # group 3 is Jacks
        plc.add_motor(axis, group=3, htype=HSW, post="i", jdist=-1000)
    # group 4 is Yaw (drive to pos limit, home on referance mark. No nominal position).
    plc.add_motor(5, group=4, htype=HSW, jdist=1000)
    plc.write(filename)

# -------PMAC 4---------
elif name == "HR":
    # Home on ref mark after driving to neg limit.
    plc = PLC(num, htype=HSW, post="i", jdist=-10000, ctype=1)
    for axis in [1, 2]:  # group 2 is Jacks
        plc.add_motor(axis, group=2, htype=HSW, post="i", jdist=-10000)
    plc.write(filename)

elif name == "S4":
    # Go to pos limit, then home off reference marks and return to initial position
    plc = PLC(num, htype=HSW_HLIM, post="i", jdist=1000, ctype=1)
    for axis in [3, 4]:  # group 2 is X1, X2
        plc.add_motor(axis, group=2)
    for axis in [5, 6]:  # group 3 is Y1, Y2
        plc.add_motor(axis, group=3)
    plc.write(filename)

elif name == "A3":
    # Home on home switch at top of travel (just under positive limit).
    plc = PLC(num, htype=HOME, post=None, ctype=1)
    plc.add_motor(7, group=2)
    plc.write(filename)

# -------PMAC 5---------
elif name == "IZERO":
    # Home on home switch at top of travel (just under positive limit). Return to initial position.
    plc = PLC(num, htype=HSW_HLIM, post="i", ctype=1)
    plc.add_motor(1, group=2)
    plc.write(filename)

elif name == "SAM1":
    plc = PLC(num, htype=HOME, post="i", ctype=1)
    plc.add_motor(2, group=2, htype=LIMIT, post="i", jdist=-1000)  # Group 2 is Y
    plc.add_motor(3, group=3, htype=LIMIT, post="i", jdist=-1000)  # Group 3 is Rot
    plc.write(filename)

elif name == "TAB1":
    plc = PLC(num, post="i", ctype=1)
    for axis in [4, 5, 6]:  # group 2 is Y1, Y2, Y3
        plc.add_motor(axis, group=2, htype=LIMIT, post="i", jdist=1000)
    for axis in [7, 8]:  # group 3 is X1, X2
        plc.add_motor(axis, group=3, htype=HSW_HLIM, post="i", jdist=1000)
    plc.write(filename)

# -------PMAC 6---------
elif name == "SAM2":
    plc = PLC(num, htype=RLIM, post=None, ctype=GEOBRICK)
    for axis in [1, 2, 3]:
        plc.add_motor(axis, group=2)
    plc.write(filename)

elif name == "SAM3":
    plc = PLC(num, htype=HOME, post=None, ctype=1)
    plc.add_motor(4, group=2)
    plc.write(filename)

# -------PMAC 7---------
elif name == "USER1":
    plc = PLC(num, htype=RLIM, post=None, ctype=GEOBRICK)
    group = 2
    for axis in [1, 2, 3, 4, 5, 6, 7, 8]:
        plc.add_motor(axis, group=group)
        group += 1
    plc.write(filename)

# -------PMAC 8 DCM brick 1---------
elif name == "DCMX":
    # Home off negative limit and return to initial position
    plc = PLC(num, htype=LIMIT, post="i", jdist=-1000, ctype=1)
    plc.add_motor(1, group=1)
    plc.write(filename)

# ------PMAC 9 DCM brick 2 --------
## HMZ encoders on 13, 14, 15 and 16 as 6 is DC motor stuff and 13-16 mirrors
## axis 5-8's input and the others are just for consistency
elif name == "DCM2":
    plc = PLC(num, post="i", ctype=GEOBRICK)
    # plc = PLC(num, ctype=GEOBRICK)
    ## Need some checks to make sure the Y slide is in position before
    ## homing the Bragg axis and vice versa
    # Bragg axis
    move_Y_to_safety = """
#define LookupTableFlag P2132
#define Motor1DesiredVelocityZero m133

LookupTableFlag=i51
cmd"i51=0"
;------move Y to neg lim switch first.
cmd"#1J-"
i5111=20*8388608/i10
while(i5111>0)			;Pause for 20 mseconds to let the move start
endw
i5111=500000*8388608/i10		;Set timer for 500 seconds
while(Motor1DesiredVelocityZero=0)
and(i5111>0)
endw
"""
    # 5, 6, 7, 8 are the Bragg encoders
    plc.add_motor(2, htype=LIMIT, group=2, post=20000000, enc_axes=[5, 6, 7, 8])
    plc.configure_group(2, pre=move_Y_to_safety, post='cmd"i51=LookupTableFlag"')
    move_Bragg_to_safety = """
#define Motor2DesiredVelocityZero m233

LookupTableFlag=i51
cmd"i51=0"
;-----Now move Bragg to some angle so as not to cause a clash when Y moves down (up in counts).

cmd"#2J=20000000"
i5111=20*8388608/i10
while(i5111>0)			;Pause for 20 mseconds to let the move start
endw
i5111=500000*8388608/i10		;Set timer for 500 seconds
while(Motor2DesiredVelocityZero=0)
and(i5111>0)
endw
"""
    plc.add_motor(1, htype=HSW, group=3, post="L", jdist=-10000)
    plc.configure_group(
        3, pre=move_Bragg_to_safety, post='cmd"#1hmz"\ncmd"i51=LookupTableFlag"'
    )
    # Pitch
    plc.add_motor(3, htype=HSW, group=4, jdist=-20000)
    # Roll
    plc.add_motor(4, htype=HSW, group=5, jdist=-20000)
    # Store the lookup table before and restore after homing
    for group_num in (4, 5):
        plc.configure_group(
            group=group_num,
            pre='LookupTableFlag=i51\n\t\tcmd "i51=0"',
            post='cmd"i51=LookupTableFlag"',
        )
    plc.write(filename)

else:
    sys.stderr.write("***Error: Can't make homing PLC %d for %s\n" % (num, name))
    sys.exit(1)
