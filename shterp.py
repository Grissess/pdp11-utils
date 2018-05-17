import struct
import sys
import cStringIO

if len(sys.argv)<2:
    print '''USAGE: python shterp.py [<options>] <tape> [<tape> [...]]

Where <tape> is a "standard binary format tape" (as with mkterp.py).

Options:
    -m <image> makes an binary image file of memory that would be the result
        of loading these tapes into empty (zeroed) memory in the specified
        order.
    -o <tape> outputs a merged tape, the result of combining all the tapes
        in the order specified. The origin PC will be the origin PC of the
        last tape that has one set to non-default (non-1). If no such tape
        exists, the output will have a default PC (1). mkterp.py with only
        the -p option can make an empty tape to force the PC to a certain
        value by including it at the end of the list.
    -s causes the program to be strict about checksums (default lenient).
'''
    exit()

mergefile = None
outtape = None
strict = False
tapes = []
setPC = 1

def csum(bytes):
    cs = 0
    for ch in bytes:
        cs = (cs + ord(ch)) % 256
    return 256 - cs

i = 1
while i < len(sys.argv):
    if sys.argv[i] == '-m':
        mergefile = open(sys.argv[i+1], 'wb')
        merge = cStringIO.StringIO()
        i += 2
    elif sys.argv[i] == '-o':
        outtape = open(sys.argv[i+1], 'wb')
        i += 2
    elif sys.argv[i] == '-s':
        strict = True
        i += 1
    else:
        break

tapes = sys.argv[i:]

for tape in tapes:
    tf = open(tape, 'rb')
    atend = False
    while True:
        hdr = tf.read(6)
        if len(hdr)<6:
            if atend:
                print '%s: End of tape. (%d/0%o/0x%x bytes extraneous data.)'%(tape, len(hdr), len(hdr), len(hdr))
            else:
                print '%s: Unexpected end of tape'%(tape,)
            break
        atend=False
        magic, size, orig = struct.unpack('<HHH', hdr)
        if magic != 1:
            print '%s: Expected 1 in header, found %d/0%o/0x%x'%(tape, magic, magic, magic)
            if strict:
                continue
        if size < 6:
            print '%s: Expected size 6 or greater, found %d/0%o/0x%x'%(tape, size, size, size)
            if strict:
                continue
        if size == 6:
            print '%s: Set PC = %d/0%o/0x%x %s'%(tape, orig, orig, orig, '(default)' if orig==1 else '')
            if orig != 1:
                setPC = orig
            atend = True
            data = ''
        if size > 6:
            print '%s: Datablock of %d/0%o/0x%x bytes to load at %d/0%o/0x%x'%(tape, size-6, size-6, size-6, orig, orig, orig)
            data = tf.read(size-6)
            if len(data) < size-6:
                print '%s: Datablock unexpectedly truncated'
                continue
        csc = csum(hdr+data)
        csf = ord(tf.read(1))
        if csc != csf:
            print '%s: Bad csum, expected %d/0%o/0x%x, got %d/0%o/0x%x'%(tape, csc, csc, csc, csf, csf, csf)
            if strict:
                continue
        else:
            print '%s: Good csum %d/0%o/0x%x'%(tape, csc, csc, csc)
        if size > 6:
            if outtape:
                outtape.write(hdr+data+chr(csc))
            if mergefile:
                merge.seek(orig)
                merge.write(data)

if mergefile:
    mergefile.write(merge.getvalue())
    mergefile.close()

if outtape:
    hdr = struct.pack('<HHH', 1, 6, setPC)
    outtape.write(hdr+chr(csum(hdr)))
    outtape.close()

print 'Completed.'
