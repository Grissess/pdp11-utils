#ODT input generator

import struct
import sys

if len(sys.argv)<2:
	print '''USAGE: python mkodt.py <tape>

Where <tape> is a "standard binary format tape" (as with mkterp.py and shterp.py).

Prints to stdout a (binary!) file consisting of the ODT commands required to set the
memory of a PDP-11 to whatever would be loaded by the tape. If the tape sets PC,
this will cause the PDP to run it, assuming HALT isn't set.
'''
	exit()

def octd(i):
        if i == 0:
                return '0'
	return oct(i)[1:]

tf = open(sys.argv[1], 'rb')
while True:
	hdr = tf.read(6)
	magic, size, orig = struct.unpack('<HHH', hdr)
	if size == 6:
		if orig != 1:
			sys.stdout.write(octd(orig)+'G')
			break
	else:
		data = tf.read(size-6)
                words = struct.unpack('<'+'H'*(len(data)/2), data)
		sys.stdout.write(octd(orig)+'/')
		sys.stdout.write('\n'.join([octd(i) for i in words])+'\r')
		csf = tf.read(1) #and screw it
