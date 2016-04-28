# ---------------------------------------------------------------------------------------
# program_panels.py
#
# Programs G3 FlyPanels. Autoincrements panels numbers
#
# Usage: python program_panels.py  [start_number] [stop_number] 
#
# Note, start_number and stop_number are optional the defaults are 1 and 127.
#
# ---------------------------------------------------------------------------------------
from __future__ import print_function
import sys
import subprocess

# Get command line arguments
if len(sys.argv) > 1:
    start_number = int(sys.argv[1])
else:
    start_number = 1

if len(sys.argv) > 2:
    stop_number = int(sys.argv[2])
else:
    stop_number = 127

if start_number <=0 or start_number > 127:
    print('Error: start_number must be > 0 and < 128')
    sys.exit(0)

if stop_number < start_number:
    print('Error: stop_number must be >= start_number')
    sys.exit(0)

if stop_number > 127:
    printf('Error: stop_number must be < 128')
    sys.exit(0)

# Program panels - from start_number to stop_number
panel_number = start_number
print()

while True:

    ans = raw_input("Current panel# {0}/{1}.  Options p=program (default), b=back, n=next, e=exit, or new panel# (1-127): ".format(panel_number,stop_number)) 
    if len(ans) == 0:
        ans = 'p'
    else:
        try:
            ans = int(ans)
            if ans > 0 and ans < 128:
                panel_number = ans
            else:
                print()
                print('Error: panel number out of range')
            print()
            continue
        except ValueError:
            ans = ans[0]

    if ans not in ('p', 'b', 'n', 'e'):
        print()
        print('Error: uknown command {0}'.format(ans))
        print()
        continue

    if ans == 'b':
        if panel_number > 1:
            panel_number -= 1
        print()
        continue
    elif ans == 'n':
        if panel_number < 127:
            panel_number += 1
        print()
        continue
    elif ans == 'e':
        print()
        break

    panel_number_hex = hex(panel_number)
    
    # Check signature
    cmd = 'sudo avrdude -c avrispmkII -p m168'
    cmd_list = cmd.split(' ')
    subprocess.call(cmd_list)
    
    # Write fuse values 
    cmd = 'sudo avrdude -c avrispmkII -p m168 -U efuse:w:0x0:m -U hfuse:w:0xd4:m -U lfuse:w:0xf7:m'
    cmd_list = cmd.split(' ')
    subprocess.call(cmd_list)
    
    # Program bootloader + erase flash
    cmd = 'sudo avrdude -c avrispmkII -p m168 -U flash:w:panel_bl.hex'
    cmd_list = cmd.split(' ')
    subprocess.call(cmd_list)
    
    # Program firmware + no erase flash
    cmd = 'sudo avrdude -c avrispmkII -p m168 -D -U flash:w:panel.hex'
    cmd_list = cmd.split(' ')
    subprocess.call(cmd_list)
    
    # Program eeprom
    cmd = 'cp eep_127.bin eep_xxx.bin'
    cmd_list = cmd.split(' ')
    subprocess.call(cmd_list)
    
    cmd0 = 'printf \\x{0}'.format(panel_number_hex[2:])
    cmd0_list = cmd0.split(' ')
    printf_popen = subprocess.Popen(cmd0_list,stdout=subprocess.PIPE)
    cmd1 = 'dd of=eep_xxx.bin bs=1 seek=0 count=1 conv=notrunc'
    cmd1_list = cmd1.split(' ')
    subprocess.call(cmd1_list,stdin=printf_popen.stdout)
    
    cmd = 'sudo avrdude -c avrispmkII -p m168 -U eeprom:w:eep_xxx.bin:r'
    cmd_list = cmd.split(' ')
    subprocess.call(cmd_list)
    
    cmd = 'rm eep_xxx.bin'
    cmd_list = cmd.split(' ')
    subprocess.call(cmd_list)

    if panel_number < stop_number:
        panel_number += 1


