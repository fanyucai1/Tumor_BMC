import re

def run(Samplesheet):
    infile=open(Samplesheet,"r")
    sample,num,counts=[],0,0
    for line in infile:
        line=line.strip()
        array=re.split(r'[,\t]',line)
        num+=1
        if line.startswith("Sample_ID"):
            counts=num
        if counts!=0:
            sample.append(array[0])
    return sample