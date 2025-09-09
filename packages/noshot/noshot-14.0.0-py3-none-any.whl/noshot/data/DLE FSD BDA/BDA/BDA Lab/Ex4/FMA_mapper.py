#usr/bin/env python

import sys

line= sys.stdin

for row in sys.stdin:
	row=row.strip().split(',')
	if len(row) > 7 :
		user_name = row[7].strip()
		binary = str(bin(abs(hash(user_name))))[2:]
		t_zeros = len(binary) - len(binary.rstrip('0'))
		print('%d' % t_zeros)

