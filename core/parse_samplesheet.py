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
        if counts!=0 and num==counts+1:
            if array[1]=="":
                sample.append(array[0])
            else:
                sample.append(array[1])
    return sample