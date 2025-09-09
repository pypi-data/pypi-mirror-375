import sys

Bloom_size = 100000
hashc = 2

bit_array = 0
def get_hashes(item, size, count):
	ip = item.split('.')
	h1 = sum(int(x) for x in ip)%size
	h2 = sum(2*int(ip[i])*i-5 for i in range(len(ip)))
	return [h1,h2]


def add_to_bloom(item):
	global bit_array
	for h in get_hashes(item, Bloom_size, hashc):
		bit_array |= 1<<h

def is_in_bloom(item):
	for h in get_hashes(item, Bloom_size, hashc):
		if bit_array & (1<<h) == 0:
			return False
	return True

for line in sys.stdin:
	ip = line.strip().split('\t')[0]
	if ip and not is_in_bloom(ip):
		add_to_bloom(ip)
		print(ip)
		
