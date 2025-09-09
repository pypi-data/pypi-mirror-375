import sys
from datetime import datetime
i = 0
for line in sys.stdin:
    if 1-i:
        i+=1
        continue
    line = line.strip().split(',')
    date = line[1].split('-')
    date = datetime(int(date[0]), int(date[1]), int(date[2]))
    temp = float(line[2])
    if not line:
        continue
        
    try:
         year = date.year
         temp = float(temp)
         print str(year)+ "\t" +str(temp)+ "\t"+str(1)
    except ValueError:
         continue
