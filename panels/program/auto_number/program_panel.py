# ---------------------------------------------------------------------------------------
# program_panels.py
#
# Programs G3 FlyPanels. Autoincrements panels numbers
#
# ---------------------------------------------------------------------------------------
from __future__ import print_function
import sys
import subprocess
from optparse import OptionParser

usage = "usage: %prog [options]"

parser = OptionParser(usage=usage)
parser.add_option('-d', '--device', dest='device', help='specify device used for avr programming, e.g. avrispmkII, stk500',  default='avrispmkII')
parser.add_option('-p', '--port', dest='port', help='specify port used by programmer, e.g usb, /dev/ttyUSB0, etc.',  default='usb')
parser.add_option('-n', '--nobootloader', action='store_true', dest='nobootloader', help='do not use/program bootloader')
parser.add_option('-s', '--startnum', dest='start_number', type='int', help='starting number for auto number increment',default=1)
parser.add_option('-f', '--finalnum', dest='final_number', type='int', help='final number for auto number increment',default=127)

(options,args) = parser.parse_args()

programmer = options.device
port = options.port
bootloader = not options.nobootloader
start_number = options.start_number
final_number = options.final_number

print()
print('Panels batch programmer')
print()
print('Options')
print('-------')
print('programmer: {0}'.format(programmer))
print('port:       {0}'.format(port))
print('bootloader: {0}'.format(bootloader))
print('start  #:   {0}'.format(start_number))
print('final  #:   {0}'.format(final_number))
print()


if start_number <=0 or start_number > 127:
    print('Error: start_number must be > 0 and < 128')
    sys.exit(0)

if final_number < start_number:
    print('Error: final_number must be >= start_number')
    sys.exit(0)

if final_number > 127:
    printf('Error: final_number must be < 128')
    sys.exit(0)


# Program panels - from start_number to final_number
panel_number = start_number
print()

while True:

    ans = raw_input("Current panel# {0}/{1}.  Options p=program (default), b=back, n=next, e=exit, or new panel# (1-127): ".format(panel_number,final_number)) 
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
    cmd = 'sudo avrdude -c {0} -P {1} -p m168'.format(programmer,port)
    cmd_list = cmd.split(' ')
    subprocess.call(cmd_list)
    
    # Write fuse values 
    if bootloader:
        cmd = 'sudo avrdude -c {0} -P {1} -p m168 -U efuse:w:0xf8:m -U hfuse:w:0xd4:m -U lfuse:w:0xf7:m'.format(programmer,port)
    else:
        cmd = 'sudo avrdude -c {0} -P {1} -p m168 -U efuse:w:0xf9:m -U hfuse:w:0xd4:m -U lfuse:w:0xf7:m'.format(programmer,port)
    cmd_list = cmd.split(' ')
    subprocess.call(cmd_list)
    
    # Program bootloader + erase flash
    if bootloader:
        cmd = 'sudo avrdude -c {0} -P {1} -p m168 -U flash:w:panel_bl.hex'.format(programmer,port)
        cmd_list = cmd.split(' ')
        subprocess.call(cmd_list)
    
    # Program firmware + no erase flash
    if bootloader:
        cmd = 'sudo avrdude -c {0} -P {1} -p m168 -D -U flash:w:panel.hex'.format(programmer,port)
    else:
        cmd = 'sudo avrdude -c {0} -P {1} -p m168 -U flash:w:panel.hex'.format(programmer,port)
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
    
    cmd = 'sudo avrdude -c {0} -P {1} -p m168 -U eeprom:w:eep_xxx.bin:r'.format(programmer,port)
    cmd_list = cmd.split(' ')
    subprocess.call(cmd_list)
    
    cmd = 'rm eep_xxx.bin'
    cmd_list = cmd.split(' ')
    subprocess.call(cmd_list)

    if panel_number < final_number:
        panel_number += 1


