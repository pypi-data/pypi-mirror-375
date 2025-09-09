import sys

def reducer():
    yearly_min = {}  
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            year, temp, _ = line.split('\t')
            temp = float(temp)
            if year in yearly_min:
                if temp < yearly_min[year]:
                    yearly_min[year] = temp
            else:
                yearly_min[year] = temp
                
        except ValueError:
            continue
    coolest_year = None
    coolest_temp = float('inf')
    for year, temp in yearly_min.items():
        if temp < coolest_temp:
            coolest_temp = temp
            coolest_year = year
    
    if coolest_year:
        print("coolest year ",str(coolest_year),"  Minimum Temperature ",str(coolest_temp))

if __name__ == "__main__":
    reducer()