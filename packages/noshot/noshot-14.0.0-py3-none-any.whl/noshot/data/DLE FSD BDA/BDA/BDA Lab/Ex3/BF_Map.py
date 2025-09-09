import sys
for line in sys.stdin:
	line = line.strip()
	if not line:
		contine
	ip = line.split(',')[0]
	try:
		int(ip.split('.')[0])
	except:
		continue
	print str(ip)+"\t"+str(1)
