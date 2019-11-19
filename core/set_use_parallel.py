import subprocess
from multiprocessing import Pool
import time

def f(cmd):
    subprocess.check_call(cmd,shell=True)

def run(shfile,shell_name):
    start=time.time()
    infile=open(shfile,"r")
    array=[]
    for line in infile:
        line=line.strip()
        array.append(line)
    pool = Pool(processes=5)
    pool.map(f,array)
    end=time.time()
    print("\n=============step:%s start================\n"%(shell_name))
    print("\nTotal elapse time is %g seconds\n" % (end - start))
    print("\n==============step:%s finished===============\n"%(shell_name))