#usr/bin/env python
import sys

max_trail = 0
for line in sys.stdin :
	line = line.strip()
	if not line : continue
	try :
		trail = int(line)
		if max_trail < trail :
			max_trail = trail
	except : continue
else:
	print("Total number of unique uids are : ",2**max_trail)
