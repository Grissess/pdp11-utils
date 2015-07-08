#PDP-11 crappy "terp" (tape) format for loading into simh/pdp11's terp dervs.

import struct
import sys

if len(sys.argv) < 2:
    print '''Usage: python mkterp.py {BLOCK} {BLOCK} {BLOCK}
where each {BLOCK} is:
	[-O <origin>] to set the origin (default 1)
	-d <file> a binary file to read in data (terminates the block).
OR:
	-o <fname> to set the output file name (last instance wins).
OR:
	-p <pc> to set the address at which the program shall start (last instance wins).
'''
    exit()

ofile = 'image.out'
pc = 1 #For some reason, 1 does not set PC to any special value on load.
blocks = [] #[{'org', 'fname'}]
org = 0

i = 1
while i < len(sys.argv):
	if sys.argv[i] == '-o':
		ofile = sys.argv[i+1]
		i+=2
	elif sys.argv[i] == '-p':
		pc = eval(sys.argv[i+1])
		i+=2
	elif sys.argv[i] == '-O':
		org = eval(sys.argv[i+1])
		i+=2
        elif sys.argv[i] == '-d':
		fname = sys.argv[i+1]
		i+=2
		blocks.append({'org': org, 'fname': fname})
		org = 0
	else:
		print 'Unrecognized option:', sys.argv[i], 'skipped'
		i+=1

print 'Blocks to be put into %s:'%(ofile,)
for block in blocks:
	print 'File', block['fname'], '@', block['org']

of = open(ofile, 'wb')
for block in blocks:
	inf = open(block['fname'], 'rb')
	data = inf.read()
	inf.close()
	pkt = struct.pack('<HHH', 1, 6+len(data), block['org'])+data
	csum = 0
	for ch in pkt:
		csum = (csum + ord(ch)) % 256
	of.write(pkt + chr(256 - csum))
pkt = struct.pack('<HHH', 1, 6, pc)
csum = 0
for ch in pkt:
	csum = (csum + ord(ch)) % 256
of.write(pkt + chr(256 - csum))
of.close()
print 'Complete.'
