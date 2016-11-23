import struct
import sys

for line in sys.stdin:
    parts = line.split()
    sys.stdout.write(struct.pack('<' + 'H' * len(parts), *(int(part, 8) for part in parts)))

sys.stdout.flush()
