import os
import sys
import time
import thread
import serial
import termios
import tty
import traceback

print '[[[Opening', sys.argv[1], ']]]'
f = serial.Serial(sys.argv[1], int(sys.argv[2]))
FD = f.fileno()
print '[[[FD=', FD, ']]]'
old = termios.tcgetattr(sys.stdin.fileno())
print '[[[Setting cbreak...]]]'
tty.setraw(sys.stdin.fileno())
print '[[[...ready]]]\r'

def write_thread(fd):
    while True:
        buffer = f.read(1)
        #print 'READ: %r'%(buffer,)
        sys.stderr.write(buffer)

thread.start_new(write_thread, (FD,))

cflag = False
cintro = '[[[^C{h,H(elp),q,Q,e,E,f,F,^C}?]]]'
cblank = '\b'*len(cintro)+' '*len(cintro)+'\b'*len(cintro)
cunknown = '\b'*(len(cintro)-5)+' '*(len(cintro)-5)+'\b'*(len(cintro)-5)+'?!]]]'
lecho = False
delay = 0.001
chelptext = '''
[[[^C mode commands:
    -h,H: this help text
    -q,Q: quit
    -e,E: toggle local echo
    -F: send local file
    -f: send local file, throttled
    -t, T: view/set throttle rate
    -^C: send ^C]]]
'''.replace('\n', '\r\n')

try:
    while True:
        buffer = sys.stdin.read(1)
        #sys.stderr.write('[[[IN:%r]]]'%(buffer,))
        if cflag:
            if buffer in ('q', 'Q'):
                raise SystemExit()
            elif buffer in ('e', 'E'):
                sys.stderr.write(cblank)
                lecho = not lecho
            elif buffer in ('h', 'H'):
                sys.stderr.write(cblank)
                sys.stderr.write(chelptext)
            elif buffer in ('t', 'T'):
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
                res = raw_input('[[[Period (currently %f), blank to keep: '%(delay,))
                if not res:
                    print 'No change.]]]'
                else:
                    delay = float(res)
                    print 'Set.]]]'
                tty.setraw(sys.stdin.fileno())
            elif buffer in ('f', 'F'):
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
                if buffer == 'F':
                    stime = 0
                else:
                    stime = delay
                fname = raw_input('[[[File: ')
                try:
                    fp = open(fname, 'rb')
                except Exception:
                    print 'File open failed:'
                    traceback.print_exc()
                else:
                    fp.seek(0, 2) #EOF
                    sz = fp.tell()
                    fp.seek(0, 0)
                    while True:
                        data = fp.read(1)
                        if fp.tell()%32 == 0 or not data:
                            print '\r'+' '*50+'\rProgress: %d/%d (%.2f%%)'%(fp.tell(), sz, 100*float(fp.tell())/sz),
                        if not data:
                            break
                        f.write(data)
                        time.sleep(stime)
                print 'Done.]]]'
                tty.setraw(sys.stdin.fileno())
            elif buffer == '\x03':
                sys.stderr.write(cblank)
                f.write(buffer)
                if lecho:
                    sys.stderr.write(buffer)
            else:
                sys.stderr.write(cunknown)
            cflag = False
        else:
            if buffer == '\x03':
                if not cflag:
                    sys.stderr.write(cintro)
                    cflag = True
            else:
                f.write(buffer)
                if lecho:
                    sys.stderr.write(buffer)
except Exception:
    traceback.print_exc()
finally:
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
