import math

class BloomFilter:
    def __init__(self, size=13):
        self.size = size
        self.bit_array = [0] * size
       
    def h1(self, x):
        return (2*x) % self.size
      
    def h2(self, x):
        return (x+10) % self.size
       
    def h3(self, x):
        return (x + 15) % self.size
       
    def add(self, element, hash_count):
        positions = []
        collisions = 0
	if hash_count >= 1:
            positions.append(self.h1(element))
        if hash_count >= 2:
            positions.append(self.h2(element))
        if hash_count >= 3:
            positions.append(self.h3(element))
           
        for pos in positions:
            if self.bit_array[pos] == 1:
                collisions += 1
            self.bit_array[pos] = 1
        return collisions
       
    def count_ones(self):
        return sum(self.bit_array)
def calculate_error_rate(x, y, z):
    return (1 - math.exp(-z * y / x)) ** z

def main():
    # Input parameters
    y = 13  # Number of bits in array
    elements = [142,87,95,153]
    x = len(elements)  # Number of elements
   
    print "Number of Elements (x):\t%d" % x
    print "Bit Array Size (y):\t%d\n" % y
   
    optimal_z = 1
    min_error = 1.0  # Initialize with maximum possible error
    for z in [1, 2, 3]:  # Test 1, 2, and 3 hash functions
        bf = BloomFilter(y)
        total_collisions = 0
       
        for element in elements:
            total_collisions += bf.add(element, z)
       
        ones = bf.count_ones()
        error = calculate_error_rate(x, y, z)
	print "Case %d: Using %d hash function(s)" % (z, z)
        print "Collisions:\t%d" % total_collisions
        print "Ones in array:\t%d/%d" % (ones, y)
        print "Error rate:\t%.4f" % error
        print "Bit array:\t%s\n" % bf.bit_array
	if error < min_error:
            min_error = error
            optimal_z = z
   
    print "Optimal number of hash functions: %d" % optimal_z
    print "Minimum error rate achieved: %.4f" % min_error

if __name__ == "__main__":
    main()
